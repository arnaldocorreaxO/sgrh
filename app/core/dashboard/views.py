import locale
import datetime
from django.db.models.aggregates import Count

from django.db.models.fields import FloatField
from django.db.models.query_utils import Q

from core.bascula.models import Categoria, Cliente, Movimiento, Producto
from core.base.models import Empresa
from core.dashboard.forms import DashboardForm
from core.security.models import Dashboard
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import TemplateView
from core.user.models import User

locale.setlocale(locale.LC_TIME, '')


class DashboardView(LoginRequiredMixin, TemplateView):
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.usuario = User.objects.filter(id=self.request.user.id).first()
		return super().dispatch(request, *args, **kwargs)

	def get_template_names(self):
		dashboard = Dashboard.objects.filter()
		if dashboard.exists():
			if dashboard[0].layout == 1:
				return 'vtcpanel.html'
		return 'hztpanel.html'

	def get(self, request, *args, **kwargs):
		request.user.set_group_session()
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		data = {}
		ck_color = '#C3B091'
		black_color = '#090910'
		try:
			action = request.POST['action']
			producto = request.POST['producto']
			sucursal = request.POST['sucursal']
			fecha = request.POST['fecha']
			# Convertir un string a datetime con formato 
			fecha = datetime.datetime.strptime(fecha, '%d/%m/%Y')\
									 .strftime('%Y-%m-%d')
			fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d')  

			now = fecha

			if action == 'search':
				data=[]				
				rows = Movimiento.objects.filter(sucursal=sucursal,fecha=fecha)\
									   .exclude(anulado=True)\
									   .order_by('-id')[0:10] 
				for row in rows:													
					data.append(row.toJSON())

			elif action == 'get_graph_1_1':
				data = []
				categorias=[]
				val_tot_toneladas_series=[]
				val_tot_toneladas_series_data=[]
				val_ctd_viajes_series=[]
				val_ctd_viajes_series_data=[]				
				'''MOVIMIENTO ASOCIADO'''
				suc_envio = 1  # Villeta
				suc_destino = 2  # Vallemi
				# print(self.request.user.sucursal.id)
				# print(term)
				if sucursal == '1':  # Usuario de Villeta
					suc_envio = 2  # Vallemi
					suc_destino = 1  # Villeta

				_where = '1=1'
				_where += f" AND bascula_movimiento.sucursal_id = {suc_envio} \
				AND bascula_movimiento.destino_id = {suc_destino} \
				AND bascula_movimiento.fecha <= '{fecha}' \
				AND bascula_movimiento.peso_neto > 0 \
				AND bascula_movimiento.id NOT IN \
				(SELECT movimiento_padre FROM bascula_movimiento\
				WHERE movimiento_padre is NOT NULL)"

				rows = Movimiento.objects.extra(where=[_where])
				
				rows = rows.values('producto__denominacion', 'cliente__denominacion', 'transporte__denominacion') \
                                    .filter()\
                                    .annotate(tot_toneladas=Sum('peso_neto', output_field=FloatField()),
                                              ctd_viajes=Count(True)) \
                                    .order_by('-tot_toneladas')
				for row in rows:
					text_denom = row['transporte__denominacion']
					if text_denom =='DEL PROVEEDOR':
						text_denom = row['cliente__denominacion']
					categorias.append(row['producto__denominacion'] + ' <br> ' +\
									  text_denom 					+ ' <br> ')
				
					# SERIES           
					val_tot_toneladas_series_data.append(row['tot_toneladas']/1000)          
					val_ctd_viajes_series_data.append(row['ctd_viajes'])
				
				val_tot_toneladas_series = {
					'name': 'Toneladas',
					'data': val_tot_toneladas_series_data,					
					'color': ck_color,
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.2f}",
											'style': {
												'fontSize': "20 + 'px'"
											}
										}
				}
				val_ctd_viajes_series = {
					'name': 'Viajes',
					'data': val_ctd_viajes_series_data,
					'color':black_color,
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.0f}",
											'style': {
												'fontSize': "20 + 'px'"
											}
										}
				}
				data = {
				'categories': categorias,
				'series': [val_tot_toneladas_series, val_ctd_viajes_series]
				}
				
			elif action == 'get_graph_1_2':
				data = []
				# hoy = datetime.datetime.now()				
				rows = Movimiento.objects.values('producto__denominacion') \
						.filter(sucursal=sucursal,fecha=now, peso_neto__gt=0)\
						.exclude(anulado=True)\
						.annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField())) \
						.order_by('-tot_recepcion')
				for row in rows:
					data.append([row['producto__denominacion'],
								 row['tot_recepcion']/1000])
				# print(rows.query)
				data = {
					'name': 'Stock de Productos',
					'type': 'pie',
					'colorByPoint': True,
					'data': data,
				}

			elif action == 'get_graph_2':
				filtrar = request.POST['filtrar']
				data = []
				categorias=[]
				val_tot_recepcion_series=[]
				val_tot_recepcion_series_data=[]
				val_ctd_recepcion_series=[]
				val_ctd_recepcion_series_data=[]
				# now = datetime.datetime.now()
				now = fecha
				
				rows = Movimiento.objects\
							.values('producto__denominacion', 'cliente__denominacion','transporte__denominacion') \
							.filter(sucursal=sucursal,fecha=now, peso_neto__gt=0)\
							.exclude(anulado=True)\
							.annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
									  ctd_recepcion=Count(True)) \
							.order_by('-tot_recepcion')
				blue_color = '#4F98CA'
				if filtrar =='true':
					# Filtar productos que no sea interno
					rows = rows.filter(producto__exact=producto)\
							#    .exclude(transporte__exact=1)
					blue_color = ck_color


				for row in rows:
					# CATEGORIAS DENOMINACION DE LOS PRODUCTOS + CLIENTES + TRANSPORTE
					text_denom = row['transporte__denominacion']
					if text_denom =='DEL PROVEEDOR':
						text_denom = row['cliente__denominacion']
					categorias.append(row['producto__denominacion'] + ' <br> ' +\
									  text_denom 					+ ' <br> ')
					 # SERIES           
					val_tot_recepcion_series_data.append(row['tot_recepcion']/1000)          
					val_ctd_recepcion_series_data.append(row['ctd_recepcion'])
				
				val_tot_recepcion_series = {
					'name': 'Toneladas',
					'data': val_tot_recepcion_series_data,
					'color':blue_color,
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.2f}",
											'style': {
												'fontSize': "20 + 'px'"
											}
										}
				}
				val_ctd_recepcion_series = {
					'name': 'Viajes',
					'data': val_ctd_recepcion_series_data,
					'color':black_color,
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.0f}",
											'style': {
												'fontSize': "20 + 'px'"
											}
										}
				}
				data = {
				'categories': categorias,
				'series': [val_tot_recepcion_series,val_ctd_recepcion_series]
				}
				# print(data)

			elif action == 'get_graph_3':
				data = []
				categorias=[]
				val_tot_recepcion_series=[]
				val_tot_recepcion_series_data=[]
				val_ctd_recepcion_series=[]
				val_ctd_recepcion_series_data=[]
				
				now = fecha
				month = now.month
				year = now.year    

				# Envia Vallemi recibe Villeta
				if producto == 2:
					cliente_id = 2 #Vallemi
					destino_id = 1 #Villeta
					
					rows = Movimiento.objects\
								.values('fecha') \
								.filter( sucursal=sucursal,
										cliente=cliente_id,
										destino=destino_id,
										producto=producto, 
										fecha__month=month, 
										fecha__year=year,
										peso_neto__gt=0)\
								.exclude(anulado=True)\
								.annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
										ctd_recepcion=Count(True)) \
								.order_by('fecha')
				else:
					rows = Movimiento.objects\
								.values('fecha') \
								.filter( sucursal=sucursal,										
										producto=producto, 
										fecha__month=month, 
										fecha__year=year,
										peso_neto__gt=0)\
								.exclude(anulado=True)\
								.annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
										ctd_recepcion=Count(True)) \
								.order_by('fecha')

				#.exclude(anulado=True)\ Este debe ir solo no combinar con otros campos la razon es que 
				# no genera de forma correcta el query 
				# NOT (anulado=True and otro_campo=1) 
				# esto es igual a (False and True) = False
				# print(rows.query)
				for row in rows:
					# CATEGORIAS Dias 1 al 31
					categorias.append(row['fecha'].strftime('%d'))
					# SERIES           
					val_tot_recepcion_series_data.append(row['tot_recepcion']/1000)          
					val_ctd_recepcion_series_data.append(row['ctd_recepcion'])
				   
				val_tot_recepcion_series = {
					'name': 'Toneladas',
					'data': val_tot_recepcion_series_data,
					# 'color':'#f9975d', #Naranja
					'color': ck_color,
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.2f}",
											'style': {
												'fontSize': "20 + 'px'"
											}
										}
				}
				val_ctd_recepcion_series = {
					'name': 'Viajes',
					'data': val_ctd_recepcion_series_data,
					'color':black_color,
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.0f}",
											'style': {
												'fontSize': "20 + 'px'"
											}
										}
				}
				data = {
				'categories': categorias,
				'series': [val_tot_recepcion_series,val_ctd_recepcion_series]
				}
				# print(data)
				# data['series'] = data
				# print(data)
			elif action == 'get_graph_4':
				data = []
				categorias=[]
				val_tot_recepcion_series=[]
				val_tot_recepcion_series_data=[]
				val_ctd_recepcion_series=[]
				val_ctd_recepcion_series_data=[]
				
				now = fecha
				year = now.year

				# Envia Vallemi recibe Villeta
				if producto == 2:
					cliente_id = 2 #Vallemi
					destino_id = 1 #Villeta

					rows = Movimiento.objects\
								.values('fecha__month') \
								.filter(sucursal=sucursal,
										cliente=cliente_id,
										destino=destino_id,
										producto=producto, fecha__year=year, peso_neto__gt=0)\
								.exclude(cliente=1)\
								.exclude(anulado=True)\
								.annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
										ctd_recepcion=Count(True)) \
								.order_by('fecha__month')
				else:
					rows = Movimiento.objects\
								.values('fecha__month') \
								.filter(sucursal=sucursal,
										producto=producto, fecha__year=year, peso_neto__gt=0)\
								.exclude(anulado=True)\
								.annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
										ctd_recepcion=Count(True)) \
								.order_by('fecha__month')

				for row in rows:
					# CATEGORIAS MESES
					#Utilizamos una fecha cualquiera para retornar solo el mes ;)
					mes = datetime.date(1900, row['fecha__month'], 1).strftime('%B').capitalize()
					categorias.append(mes)
					# SERIES           
					val_tot_recepcion_series_data.append(row['tot_recepcion']/1000)          
					val_ctd_recepcion_series_data.append(row['ctd_recepcion'])
				
				val_tot_recepcion_series = {
					'name': 'Toneladas',
					'data': val_tot_recepcion_series_data,
					# 'color':'#a9ff96', #Verde Limon
					'color': ck_color,			
					'dataLabels': {
											'enabled': 'true',
											'format': "<b>{point.y:.2f}",                          
											'style': {
												'fontSize': '14px'
											}
										}
				}
				val_ctd_recepcion_series = {
					'name': 'Viajes',
					'data': val_ctd_recepcion_series_data,
					'color':black_color,
					'dataLabels': {
											'enabled': 'true',                                            
											'format': "<b>{point.y:.0f}",
											'style': {
												'fontSize': '14px'
											}
										}
				}
				data = {
				'categories': categorias,
				'series': [val_tot_recepcion_series,val_ctd_recepcion_series]
				}

				# print(data)

			elif action == 'get_graph_5':
				now = fecha
				rows = Movimiento.objects \
									.values('producto__denominacion', 'cliente__denominacion','transporte__denominacion') \
									.filter(sucursal=sucursal,fecha=now)\
									.exclude(anulado=True)\
									.annotate(vehiculo_entrada_count=Count('id'),
											  vehiculo_salida_count=Count('id', filter=Q(peso_neto__gt=0)),
											  vehiculo_pendiente_count=Count('id', filter=Q(peso_neto=0))) \
									.order_by('producto__denominacion')
				# print(dataset)

				categorias = list()
				vehiculo_entrada_series_data = list()
				vehiculo_salida_series_data = list()
				vehiculo_pendiente_series_data = list()

				for row in rows:
					text_denom = row['transporte__denominacion']
					if text_denom == 'DEL PROVEEDOR':
						text_denom = row['cliente__denominacion']                    

					categorias.append(
						'%s <br> %s' % (row['producto__denominacion'],
										text_denom
										))
					vehiculo_entrada_series_data.append(
						row['vehiculo_entrada_count'])
					vehiculo_salida_series_data.append(
						row['vehiculo_salida_count'])
					vehiculo_pendiente_series_data.append(
						row['vehiculo_pendiente_count'])

				vehiculo_entrada_series = {
					'name': 'Entraron',
					'data': vehiculo_entrada_series_data,
					# 'color': 'green'
				}

				vehiculo_salida_series = {
					'name': 'Salieron',
					'data': vehiculo_salida_series_data,
					# 'color': 'red'
				}

				vehiculo_pendiente_series = {
					'name': 'Pendientes',
					'data': vehiculo_pendiente_series_data,
					# 'color': 'red'
				}

				data = {
					'xAxis': {'categories': categorias},
					'series': [vehiculo_entrada_series, vehiculo_salida_series, vehiculo_pendiente_series]
				}			
			else:
				data['error'] = 'Ha ocurrido un error'
		except Exception as e:
			data['error'] = str(e)
		return JsonResponse(data, safe=False)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		usu_sucursal = self.usuario.sucursal.id
		context['title'] = 'Panel de administración'
		context['fecha_actual'] = datetime.datetime.today().strftime("%d/%m/%Y")
		context['fecha_hora_actual'] = datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
		context['mes_actual'] = datetime.datetime.today().strftime("%B").capitalize()
		context['anho_actual'] = datetime.datetime.today().strftime("%Y")
		context['empresa'] = Empresa.objects.first()
		context['clientes'] = Cliente.objects.exclude(activo=False).count()
		context['destinos'] = Cliente.objects.filter(ver_en_destino=True).exclude(activo=False).count()
		context['categorias'] = Categoria.objects.exclude(activo=False).count()
		context['productos'] = Producto.objects.exclude(activo=False).count()
		# context['rows'] = Movimiento.objects.filter(sucursal=usu_sucursal).exclude(anulado=True).order_by('-id')[0:10]   
		context['usuario'] = self.usuario
		context['form'] = DashboardForm()
		return context


@requires_csrf_token
def error_404(request, exception):
	return render(request, '404.html', {})


@requires_csrf_token
def error_500(request, exception):
	return render(request, '500.html', {})
