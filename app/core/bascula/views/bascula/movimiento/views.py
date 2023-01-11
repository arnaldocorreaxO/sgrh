#SYSTEM
import json
import math
import os
import datetime

from config import settings
from core.bascula.forms import (ChoferForm, MovimientoEntradaForm, MovimientoForm,
								MovimientoSalidaForm, SearchForm, VehiculoForm)
#from core.bascula.views.bascula.vehiculo.views import VehiculoList
#LOCALS
from core.views import printSeparador
from core.bascula.models import Chofer, Cliente, ClienteProducto, ConfigSerial, Movimiento, Producto, Vehiculo
from core.base.comserial import *
from core.base.models import Empresa
from core.security.mixins import PermissionMixin

#DJANGO
#from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from django.views.generic.edit import FormView
from weasyprint import CSS, HTML


def search_select2(self,request,*args,**kwargs):
	data = []
	action = request.POST['action']
	if action == 'search_movi_asociado':		
		term = request.POST['term']
		'''MOVIMIENTO ASOCIADO'''
		suc_envio = 1  # Villeta
		suc_destino = 2  # Vallemi
		# print(self.request.user.sucursal.id)
		# print(term)
		if self.request.user.sucursal.id == 1:  # Usuario de Villeta
			suc_envio = 2  # Vallemi
			suc_destino = 1  # Villeta
		
		_where = '1=1'
		_where += f" AND bascula_movimiento.sucursal_id = {suc_envio} \
					 AND bascula_movimiento.destino_id = {suc_destino} \
					 AND bascula_movimiento.id NOT IN \
					(SELECT movimiento_padre FROM bascula_movimiento\
					 WHERE movimiento_padre is NOT NULL)"
		qs = Movimiento.objects.extra(where=[_where])
		# print(qs)
		if len(term):
			if term.isnumeric():
				qs = qs.filter(Q(nro_ticket__exact=term) |
							   Q(chofer__codigo__exact=term))
			else:
				qs = qs.filter(	Q(vehiculo__matricula__icontains=term) |
								Q(chofer__nombre__icontains=term) |
								Q(chofer__apellido__icontains=term))\
					.exclude(anulado=True)\
					.order_by('id')
		print(qs.query)
		for i in qs[0:10]:
			item = i.toJSON()
			item['text'] = str(i)
			data.append(item)
	
	elif action == 'search_vehiculo':		
		term = request.POST['term']
		qs = Vehiculo.objects.filter(Q(activo__exact=True) &
									Q(matricula__icontains=term))[0:10]
		for i in qs:
			item = i.toJSON()
			item['text'] = i.get_full_name()
			data.append(item)

	elif action == 'search_chofer':
		term = request.POST['term']
		qs = Chofer.objects.filter(Q(activo__exact=True) &
								Q(codigo__icontains=term) |
								Q(nombre__icontains=term) |
								Q(apellido__icontains=term))[0:10]
		for i in qs:
			item = i.toJSON()
			item['text'] = i.get_full_name()
			data.append(item)

	elif action == 'search_cliente':
		term = request.POST['term']	
		qs = Cliente.objects.filter(Q(activo__exact=True) &
									Q(codigo__icontains=term) |
									Q(denominacion__icontains=term))[0:10]
		for i in qs:
			item = i.toJSON()
			item['text'] = i.get_full_name()
			data.append(item)
	
	elif action == 'search_producto':
		# print(request.POST)
		if 'cliente[]' in request.POST:
			cliente = request.POST['cliente[]']
		else:
			cliente = request.POST['cliente']	
	
		term = request.POST['term']	

		if cliente:
			qs = ClienteProducto.objects.filter(sucursal__id__exact = self.request.user.sucursal.id,
												cliente__id__exact=cliente,
												producto__denominacion__icontains=term)\
										.distinct()
			# print(qs.query)
			for rows in qs:			
				row = rows.toJSON()				
				producto = row['producto']				
				# print(row)
				for p in producto:
					item={}
					# print(p.items())
					for k,v in p.items():
						# print(term)
						# print(v)
						if k =='denominacion':
							if term.upper() in v:				
								item['id'] = p['id']
								item['text'] = p['denominacion']
								# print(k,':',v)
								data.append(item)
								# print(data)
		else:
			qs = Producto.objects.filter(Q(activo__exact=True) &
										 Q(codigo__icontains=term) |	
										 Q(denominacion__icontains=term))[0:10]
			# print(qs.query)
			for i in qs:
				item = i.toJSON()
				# print(item)
				item['text'] = str(i)				
				data.append(item)
	
	return data 

"""LISTADO DE MOVIMIENTO DE BASCULA"""
class MovimientoList(PermissionMixin,FormView):	
	model = Movimiento
	template_name = 'movimiento/list.html'
	permission_required = 'view_movimiento'
	form_class = SearchForm
	
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
		
	def post(self,request,*args,**kwargs):
		data ={}		
		try:
			action = request.POST['action']
			suc_usuario = self.request.user.sucursal.id
			if action == 'search':
				data =[]
				start_date = request.POST['start_date']
				end_date = request.POST['end_date']
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None

				transporte = ",".join(transporte) if transporte!=[''] else None
				cliente = ",".join(cliente)  if cliente!= [''] else None
				destino = ",".join(destino)  if destino!=[' '] else None
				producto = ",".join(producto) if producto!=[''] else None
				vehiculo = ",".join(vehiculo)  if vehiculo!=[' '] else None
				chofer = ",".join(chofer) if chofer!=[''] else None

				_start = request.POST['start']
				_length = request.POST['length']
				_search = request.POST['search[value]']

				_where = '1 = 1'
				id_mov = None
				nro_ticket = None

				if len(_search):
					if _search.isnumeric():
						id_mov = _search
						nro_ticket = _search
						_search=''
				
				if id_mov:
					_where += f" AND bascula_movimiento.id = ({id_mov})"
				if nro_ticket:
					_where += f" OR bascula_movimiento.nro_ticket = ({nro_ticket})"				
				if transporte:
					_where += f" AND bascula_movimiento.transporte_id IN ({transporte})"
				if cliente:
					_where += f" AND bascula_movimiento.cliente_id IN ({cliente})"
				if destino:
					_where += f" AND bascula_movimiento.destino_id IN ({destino})"
				if producto:
					_where += f" AND bascula_movimiento.producto_id IN ({producto})"
				if chofer:
					_where += f" AND bascula_movimiento.chofer_id IN ({chofer})"
				if vehiculo:
					_where += f" AND bascula_movimiento.vehiculo_id IN ({vehiculo})"
				
				if len(start_date) and len(end_date):
					#Para los movimientos del dia excluimos los anulados del día
					qs = Movimiento.objects.filter(sucursal=suc_usuario,fecha__range=(start_date,end_date))\
										   .exclude(anulado=True)
				else:
					#Todos los movimientos incluyendo los anulados 
					qs = Movimiento.objects.filter(sucursal=suc_usuario)
										   

				#print(_where)
				if not _search:
					qs = qs.filter()\
					.extra(where=[_where])\
					.order_by('-id')
				else:
					qs = qs.filter( Q(chofer__nombre__icontains=_search)|
									Q(chofer__apellido__icontains=_search)|
									Q(vehiculo__matricula__icontains=_search)|
									Q(producto__denominacion__icontains=_search))
				total = qs.count()
				#print(qs.query)

				if _start and _length:
					start = int(_start)
					length = int(_length)
					page = math.ceil(start / length) + 1
					per_page = length
				
				if _length== '-1':
					qs = qs[start:]
				else:
					qs = qs[start:start + length]

				position = start + 1

				for i in qs:
					item = i.toJSON()
					item['position'] = position
					data.append(item)
					position += 1

				data = {'data': data,
						'page': page,  # [opcional]
						'per_page': per_page,  # [opcional]
						'recordsTotal': total,
						'recordsFiltered': total, }
			else:	
				data['error']= 'No ha ingresado a ninguna opción'
		except Exception as e:
			data['error'] = str(e)
		# return JsonResponse(data,safe=False)
		return HttpResponse(json.dumps(data), content_type='application/json')

	
	def get_context_data(self, **kwargs):		
		context = super().get_context_data(**kwargs)		
		context['usu_change_movimiento'] = 'SI' if self.request.user.has_perm('bascula.change_movimiento') else 'NO'
		context['title'] = ' Movimiento de Bascula'
		context['create_url'] = reverse_lazy('movimiento_create')
		context['list_url'] = reverse_lazy('movimiento_list')
		context['entity'] = 'Movimiento'
		return context


"""CREAR MOVIMIENTO DE BASCULA"""
class MovimientoCreate(PermissionMixin,CreateView):
	model = Movimiento
	form_class=MovimientoEntradaForm
	success_url = reverse_lazy('movimiento_list')
	template_name = 'movimiento/create_ent_sal.html'
	permission_required = 'add_movimiento'	

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	
	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()
			if type == 'nro_ticket':
				if not obj=='0': #Ticket Cero puede repetirse
					if Movimiento.objects.filter(nro_ticket=obj):
						data['valid'] = False
			elif type == 'peso_entrada':
				if float(obj) <= 0.00:
					data['valid'] = False
			elif type == 'vehiculo':
				if not Vehiculo.objects.filter(id=obj):
					data['valid'] = False
			elif type == 'chofer':
				if not Chofer.objects.filter(id=obj):
					data['valid'] = False
			elif type == 'cliente':
				if not Cliente.objects.filter(id=obj):
					data['valid'] = False
			elif type == 'producto':
				if not Producto.objects.filter(id=obj):
					data['valid'] = False
		except:
			pass
		return JsonResponse(data)	

	def post(self, request, *args, **kwargs):
		data = {}
		# print(request.method)
		try:
			action = request.POST['action']			
			if action == 'add':
				with transaction.atomic():
					# form = self.get_form()
					# data = form.save()
					import datetime
					movi = Movimiento()
					movi.fecha = datetime.datetime.now()
					movi.sucursal_id = request.POST['suc_usuario']					
					movi.nro_ticket = request.POST['nro_ticket']
					movi.peso_entrada = request.POST['peso_entrada']
					movi.vehiculo_id = request.POST['vehiculo']
					movi.chofer_id = request.POST['chofer']
					movi.transporte_id = request.POST['transporte']
					movi.cliente_id = request.POST['cliente']
					movi.producto_id = request.POST['producto']
					movi.destino_id = request.POST['destino']
					movi.nro_mic = request.POST['nro_mic'] if request.POST['nro_mic']!='' else None					
					movi.nro_remision = request.POST['nro_remision']
					movi.peso_embarque = request.POST['peso_embarque']
					movi.referencia = request.POST['referencia']
					movi.movimiento_padre = request.POST['movimiento_padre'] if request.POST['movimiento_padre']!='' else None
					movi.save()					
					data = {'id':movi.id}
					# Actualizamos si hay cambio de Tranportadora
					vehiculo = Vehiculo.objects.filter(id=movi.vehiculo_id).first()
					vehiculo.transporte_id = movi.transporte_id
					vehiculo.save()

			elif action == 'validate_data':
				return self.validate_data()		

			elif action == 'create-vehiculo':
				with transaction.atomic():
					frmVehiculo = VehiculoForm(request.POST)
					data = frmVehiculo.save()

			elif action == 'create-chofer':
				with transaction.atomic():
					frmChofer = ChoferForm(request.POST)
					data = frmChofer.save()

			elif action == 'search_data_movi_asociado':				
				import datetime
				data = {}
				if request.POST['id']:
					suc_usuario = request.POST['suc_usuario']
					movi = Movimiento.objects.filter(id=request.POST['id']).first()
					if movi:
						# MOVIMIENTO ASOCIADO					
						data['movi_asoc'] = movi.toJSON()
						
						# VEHICULO
						data_options = [{'id': '', 'text': '------------'}]	
						qs = Vehiculo.objects.filter(id=movi.vehiculo_id)		
						for i in qs:
							data_options.append({'id': i.id, 'text': str(i)})
						# print(data_options)
						data['vehiculo_options'] = data_options
						
						# CHOFER
						data_options = [{'id': '', 'text': '------------'}]	
						qs = Chofer.objects.filter(id=movi.chofer_id)		
						for i in qs:
							data_options.append({'id': i.id, 'text': str(i)})
						# print(data_options)
						data['chofer_options'] = data_options
						
						# CLIENTE
						data_options = [{'id': '', 'text': '------------'}]	
						qs = Cliente.objects.filter(id=movi.cliente_id)		
						for i in qs:
							data_options.append({'id': i.id, 'text': str(i)})
						# print(data_options)
						data['cliente_options'] = data_options
						
						# PRODUCTO
						data_options = [{'id': '', 'text': '------------'}]	
						qs = Producto.objects.filter(id=movi.producto_id)		
						for i in qs:
							data_options.append({'id': i.id, 'text': str(i)})
						# print(data_options)
						data['producto_options'] = data_options


			elif action == 'search_data_vehiculo':				
				import datetime
				data = {}
				peso_tara = 0
				if request.POST['id']:
					suc_usuario = request.POST['suc_usuario']
					movi_aso_sel = request.POST['movi_aso_sel']
					vehiculo = Vehiculo.objects.filter(id=request.POST['id']).first()
					movimiento = Movimiento.objects.filter(sucursal = suc_usuario,
														   fecha = datetime.datetime.now() ,
														   vehiculo = vehiculo)\
													.exclude(anulado=True)\
													.order_by('-id')
					if movimiento:
						peso_tara = movimiento.first().peso_tara
						if not peso_tara > 0:
							data['error'] = 'Movimiento de Entrada ya está registrado para el vehiculo %s' % (vehiculo)

					data['peso'] = peso_tara
					data['transporte_id'] = vehiculo.transporte.id
					# Retornamos data como diccionario y recuperos directo data['peso']
					# Si enviamos como lista de diccionarios debemos definir una lista 
					# data[] y usar append
					# data.append({'peso':movimiento.first().peso_tara}) y recuperar
					# data[0]['peso'], pero en este caso solo enviamos una clave y valor 											
					# print(data)

					'''MOVIMIENTO ASOCIADO'''
					# print(movi_aso_sel)
					if not movi_aso_sel:
						suc_envio   = 1 #Villeta
						suc_destino = 2 #Vallemi		
						if suc_usuario == '1': #Usuario de Villeta 
							suc_envio   = 2 #Vallemi
							suc_destino = 1 #Villeta						

						#BUSCAMOS MOVIMIENTO REMITENTE ORIGEN
						movi = Movimiento.objects.filter(sucursal_id = suc_envio,
														 destino = suc_destino,
														 movimiento_padre__isnull=True,
														 vehiculo=vehiculo)\
														.exclude(anulado=True)\
														.order_by('-id').first()
						if movi:
							#BUSCAMOS SI EL MOVIMIENTO YA FUE ASOCIADO
							movi_aso = Movimiento.objects.filter(movimiento_padre=movi.id).first()
							#SI NO FUE ASOCIADO, EL VEHICULO TIENE UN MOVIMIENTO ASOCIADO SIN RECEPCIONAR
							if not movi_aso:						
								data['error'] = 'El vehiculo ingresado tiene un movimiento asociado \n%s' % (movi)
					# print(data)
			else:
				# SEARCH SELECT2
				data = search_select2(self, request, *args, **kwargs)	

		except Exception as e:
			data['error'] = str(e)
		return JsonResponse(data,safe=False)
		# return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Entrada Bascula'
		context['form'] = MovimientoEntradaForm(user=self.request.user)
		context['entity'] = 'Bascula'
		context['list_url'] = self.success_url
		context['action'] = 'add'
		context['suc_usuario'] = suc_usuario		
		context['frmVehiculo'] = VehiculoForm()
		context['frmChofer'] = ChoferForm()
		config = ConfigSerial.objects.values('puerto').filter(activo=True,sucursal=suc_usuario,cod__exact='BSC1').first()
		context['puerto_bascula1'] = config['puerto'] if config else None
		config = ConfigSerial.objects.values('puerto').filter(activo=True,sucursal=suc_usuario,cod__exact='BSC2').first()
		context['puerto_bascula2'] = config['puerto'] if config else None	
		return context


"""ACTUALIZAR MOVIMIENTO DE SALIDA DE BASCULA"""
class MovimientoUpdateSalida(PermissionMixin,UpdateView):
	model = Movimiento
	form_class=MovimientoSalidaForm
	success_url = reverse_lazy('movimiento_list')
	template_name = 'movimiento/create_ent_sal.html'
	permission_required = 'change_movimiento_salida'
	
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.tipo_salida = kwargs['tipo_salida']
		return super().dispatch(request, *args, **kwargs)

	def get_object(self, queryset=None):
		# Una vez tenga PESO NETO ya no se puede modificar la salida
		try:		
			obj = self.model.objects.get(pk=self.kwargs['pk'],peso_neto__exact=0)
			return obj
		except self.model.DoesNotExist:
			raise Http404("INFORMACION: Movimiento de Bascula NO existe o ya fue realizada la SALIDA")

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()
			if type == 'nro_ticket':
				if not obj=='0': #Ticket Cero puede repetirse
					if Movimiento.objects.filter(nro_ticket=obj):
						data['valid'] = False
			elif type == 'peso_salida':
				if float(obj) <= 0.00:
					data['valid'] = False
			elif type == 'vehiculo':
				if not Vehiculo.objects.filter(id=obj):
					data['valid'] = False
			elif type == 'chofer':
				if not Chofer.objects.filter(id=obj):
					data['valid'] = False
			elif type == 'cliente':
				if not Cliente.objects.filter(id=obj):
					data['valid'] = False
			elif type == 'producto':
				if not Producto.objects.filter(id=obj):
					data['valid'] = False
		except:
			pass
		return JsonResponse(data)	

	def post(self, request, *args, **kwargs):
		data = {}
		try:
			action = request.POST['action']	
			if action == 'edit':
				with transaction.atomic():
					# form = self.get_form()
					# data = form.save()
					import datetime
					movi = self.get_object()
					nro_ticket =request.POST['nro_ticket']
					peso_salida = int(request.POST['peso_salida'])
					if peso_salida > 0:
						if movi.peso_entrada > peso_salida:
							movi.peso_neto = movi.peso_entrada - peso_salida
							movi.peso_bruto = movi.peso_entrada
							movi.peso_tara = peso_salida
							movi.tip_movimiento = 'E'
						else:
							movi.peso_neto = peso_salida - movi.peso_entrada
							movi.peso_bruto = peso_salida
							movi.peso_tara = movi.peso_entrada
							movi.tip_movimiento = 'S'
					# if movi.peso_salida > 0:
					# 	if movi.peso_entrada > movi.peso_salida:
					# 		movi.peso_neto = movi.peso_entrada - movi.peso_salida
					# 		movi.peso_bruto = movi.peso_entrada
					# 		movi.peso_tara = movi.peso_salida
					# 		movi.tip_movimiento = 'E'
					# 	else:
					# 		movi.peso_neto = movi.peso_salida - movi.peso_entrada
					# 		movi.peso_bruto = movi.peso_salida
					# 		movi.peso_tara = movi.peso_entrada
					# 		movi.tip_movimiento = 'S'
					movi.nro_ticket = nro_ticket
					movi.peso_salida = peso_salida					
					# movi.fec_salida = movi.fec_modificacion
					movi.fec_salida = datetime.datetime.now()
					movi.save()
					data['id'] = movi.id
					
			elif action == 'validate_data':
				return self.validate_data()
			else:
				data['error'] = 'No ha ingresado a ninguna opción'
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = '%s %s' % ('Salida Bascula Camión',str(self.tipo_salida).capitalize())
		# context['form'] = MovimientoSalidaForm(user=self.request.user)
		context['entity'] = 'Bascula'
		context['list_url'] = self.success_url
		context['action'] = 'edit'
		context['suc_usuario'] = suc_usuario		
		context['frmVehiculo'] = VehiculoForm()
		context['frmChofer'] = ChoferForm()
		config = ConfigSerial.objects.values('puerto').filter(activo=True,sucursal=suc_usuario,cod__exact='BSC1').first()
		context['puerto_bascula1'] = config['puerto'] if config else None
		config = ConfigSerial.objects.values('puerto').filter(activo=True,sucursal=suc_usuario,cod__exact='BSC2').first()
		context['puerto_bascula2'] = config['puerto'] if config else None	
		context['tipo_salida'] = self.tipo_salida
		return context

'''MODIFICAR MOVIMIENTO DE BASCULA TODOS LOS CAMPOS'''
class MovimientoUpdate(PermissionMixin, UpdateView):
	model = Movimiento
	template_name = 'movimiento/create.html'
	form_class = MovimientoForm
	success_url = reverse_lazy('movimiento_list')
	permission_required = 'change_movimiento'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()
			id = self.get_object().id
			if type == 'denominacion':
				if Chofer.objects.filter(denominacion__iexact=obj).exclude(id=id):
					data['valid'] = False
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST['action']
		try:
			if action == 'edit':
				data = self.get_form().save()
			elif action == 'validate_data':
				return self.validate_data()
			else:
				data['error'] = 'No ha seleccionado ninguna opción'
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context['list_url'] = self.success_url
		context['title'] = 'Edición de un Movimiento'
		context['action'] = 'edit'
		return context

'''ELIMINAR MOVIMIENTO DE BASCULA'''
class MovimientoDelete(PermissionMixin, DeleteView):
	model = Movimiento
	template_name = 'bascula/movimiento/delete.html'
	success_url = reverse_lazy('movimiento_list')
	permission_required = 'delete_movimiento'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		data = {}
		try:
			self.get_object().delete()
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = 'Notificación de eliminación'
		context['list_url'] = self.success_url
		return context

"""PRUEBAS DE LECTURA"""
def test_bascula(request):
	return render(
		request=request,
		template_name='bascula/bascula.html',
	)

"""OBTENER PESO DIRECTAMENTE DEL PUERTO SERIAL"""
@method_decorator(csrf_exempt)
def leer_puerto_serial(request,puerto):
	config = ConfigSerial.objects.get(puerto=puerto)	
	buffer = leerPuertoSerial(config)
	printSeparador()
	print('# BUFFER DATO DIRECTO SERIAL')	
	print(buffer)
	if 'error' in buffer:
		return JsonResponse({'error': buffer})
	if buffer:
		suc_usuario = request.user.sucursal.id		
		data = getPeso(suc_usuario,config,buffer)
	printSeparador()
	print('Resultado\t:', data)
	printSeparador()
	return JsonResponse({ 'peso': data })          

"""OBTENER PESO DE ARCHIVO TXT"""
@method_decorator(csrf_exempt)
def leer_peso_bascula(request):
	data = 0
	if os.path.exists("peso.txt"):
		with open("peso.txt", "r") as archivo:
			archivo.seek(0)
			linea = archivo.readline()
			print(linea)
			if linea: 
				data = float(linea[29:8])
				print(data)
				#os.remove("peso.txt")			
	return JsonResponse({ 'peso': data })          

def getPeso(suc_usuario,config,buffer):
	# VILLETA
	if suc_usuario == 1: 
		"""OBTENER VALORES DEL BUFFER DE LA BASCULA 1"""
		# VISOR BALPAR
		if config.cod == 'BSC1' or config.cod == 'BSC2': 
			pos_ini = buffer.find('+') + 1
			print('Posicion Inicial:', pos_ini)
			pos_fin = pos_ini + (config.pos_fin - config.pos_ini)
			print('Posicion Final\t:', pos_fin)
			return buffer[pos_ini:pos_fin]
		
		"""OBTENER VALORES DEL BUFFER DE LA BASCULA 2"""
		# VISOR TOLEDO DESHABILITADO
		if config.cod == 'BSC2' and True == False: #Para el simulador habilitar este 
			pos_ini = config.pos_ini
			print('Posicion Inicial:', pos_ini)
			pos_fin = config.pos_fin
			print('Posicion Final\t:', pos_fin)
			return buffer[pos_ini:pos_fin]
	# VALLEMI
	elif suc_usuario == 2: 
		"""OBTENER VALORES DEL BUFFER DE LA BASCULA 1"""
		# VISOR SIPEL ORION
		if config.cod == 'BSC1': 
			pos_ini = config.pos_ini
			print('Posicion Inicial:', pos_ini)
			pos_fin = config.pos_fin
			print('Posicion Final\t:', pos_fin)
			return buffer[pos_ini:pos_fin]
		
		"""OBTENER VALORES DEL BUFFER DE LA BASCULA 2"""
		# VISOR SIPEL ORION
		if config.cod == 'BSC2': 
			pos_ini = config.pos_ini
			print('Posicion Inicial:', pos_ini)
			pos_fin = config.pos_fin
			print('Posicion Final\t:', pos_fin)
			return buffer[pos_ini:pos_fin]


'''IMPRESION DE TICKET'''
class MovimientoPrint(View):
	success_url = reverse_lazy('movimiento_list')

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	@method_decorator(csrf_exempt)
	def get_height_ticket(self):
		movimiento = Movimiento.objects.get(pk=self.kwargs['pk'])
		height = 180		
		# increment = movimiento.all().count() * 5.45
		increment = 1 * 5.45
		height += increment
		print(round(height))
		return round(height)		
	
	@method_decorator(csrf_exempt)
	def get(self, request, *args, **kwargs):
		data = {}
		try:
			movimiento = Movimiento.objects.filter(pk=self.kwargs['pk'],fec_impresion__isnull=True).first()
			if movimiento:
				if 'print_ticket' in request.GET:
					#Permitir imprimir una vez en la llamada de ajax
					pass					
				else:
					movimiento.fec_impresion = datetime.datetime.now()
					if movimiento.peso_neto > 0: 
						movimiento.save()
					context = {'movimiento': movimiento, 'company': Empresa.objects.first()}
					context['height'] = self.get_height_ticket()
					template = get_template('movimiento/ticket.html')
					html_template = template.render(context).encode(encoding="UTF-8")
					url_css = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.3.1/css/bootstrap.min.css')
					pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(
						stylesheets=[CSS(url_css)], presentational_hints=True)
					response = HttpResponse(pdf_file, content_type='application/pdf')
					# response['Content-Disposition'] = 'filename="generate_html.pdf"'
					return response
			else:
				data['info'] ='La impresión ya fue realizada'
				return HttpResponse(json.dumps(data), content_type='application/json')
			
		except Exception as e:
			print(str(e))
		return HttpResponseRedirect(self.success_url)


