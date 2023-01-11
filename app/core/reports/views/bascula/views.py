import datetime
import json
from core.bascula.views.bascula.movimiento.views import search_select2

from core.reports.forms import ReportForm
from core.reports.jasperbase import JasperReportBase
from core.security.mixins import ModuleMixin
from core.security.models import Module
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

'''REPORTE 001'''
class RptBascula001ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula001.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']	#Tipo pdf o xls
		data = {}
		try:
			if action == 'report':
				data = []
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()					
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None			
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None		
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula001'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'MOVIMIENTO DE PRODUCTOS POR CLIENTE Y PRODUCTO'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta
				
				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Movimiento de Bascula agrupado por Cliente y Producto'
		context['action'] = 'report' 
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 002'''
class RptBascula002ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula001.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']	#Tipo pdf o xls
		data = {}
		try:
			if action == 'report':
				data = []
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()				
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None	
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None	
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula002'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'MOVIMIENTO DE PRODUCTOS POR VEHICULO Y PRODUCTO'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta

				return report.render_to_response(tipo)
			
			# SEARCH SELECT2
			rtn = search_select2(action,request)
			if rtn:
				data = rtn

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Movimiento de Bascula agrupado por Vehiculo y Producto'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 003'''
class RptBascula003ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula001.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']
		data = {}
		try:
			if action == 'report':
				data = []
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()				
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None	
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula003'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'MOVIMIENTO DE PRODUCTOS POR CLIENTE Y PRODUCTO'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta

				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Movimiento de Bascula agrupado por Cliente y Producto en Toneladas'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 004'''
class RptBascula004ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula004.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']
		data = {}
		try:
			if action == 'report':
				data = []
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()				
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				# vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				# chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None	
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula004'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'INFORME DE TOTAL DE PRODUCTOS POR CLIENTES'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				# report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				# report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta

				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Total de Productos por Clientes'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 005'''		
class RptBascula005ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula004.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']
		data = {}
		try:
			if action == 'report':
				data = []
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()				
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				# vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				# chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None	
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula005'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'INFORME DE TOTAL DE PRODUCTOS POR CLIENTES'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				# report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				# report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta

				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Total de Productos por Clientes'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 006'''
class RptBascula006ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula006.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']
		data = {}
		try:
			if action == 'report':
				data = []
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()				
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None
				situacion = request.POST['situacion']
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula006'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'INFORME DE VEHICULOS EN TRANSITO'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_SITUACION'] = situacion if len(situacion)!=0 else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta

				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Vehiculos en Transito'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 007'''
class RptBascula007ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula007.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']	#Tipo pdf o xls
		data = {}
		try:
			if action == 'report':
				data = []
				# Rango de Fecha
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()
				# Rango de Hora de Entrada				
				time_range_in = request.POST['time_range_in']
				hora_ent_desde = time_range_in[:8].strip()
				hora_ent_hasta = time_range_in[10:].strip()	
				# Rango de Hora de Salida			
				time_range_out = request.POST['time_range_out']
				hora_sal_desde = time_range_out[:8].strip()
				hora_sal_hasta = time_range_out[10:].strip()			
		
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				# vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				# chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None	
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula007'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'INFORME DIARIO TOTALES POR CLIENTES Y PRODUCTOS'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				# report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				# report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta
				report.params['P_HORA_ENT_DESDE'] = hora_ent_desde
				report.params['P_HORA_ENT_HASTA'] = hora_ent_hasta
				report.params['P_HORA_SAL_DESDE'] = hora_sal_desde
				report.params['P_HORA_SAL_HASTA'] = hora_sal_hasta

				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Resumen de Totales por Clientes y Productos'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context

'''REPORTE 008'''
class RptBascula008ReportView(ModuleMixin, FormView):
	template_name = 'bascula/reports/rpt_bascula008.html'
	form_class = ReportForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		action = request.POST['action']
		tipo = request.POST['tipo']
		data = {}
		try:
			if action == 'report':
				data = []	
				# Rango de Fecha
				date_range = request.POST['date_range']
				fecha_desde = date_range[:11].strip()
				fecha_hasta = date_range[13:].strip()		
				sucursal = request.POST.getlist('sucursal') if 'sucursal' in request.POST else None			
				transporte = request.POST.getlist('transporte') if 'transporte' in request.POST else None			
				cliente = request.POST.getlist('cliente') if 'cliente' in request.POST else None			
				destino = request.POST.getlist('destino') if 'destino' in request.POST else None
				producto = request.POST.getlist('producto') if 'producto' in request.POST else None	
				vehiculo = request.POST.getlist('vehiculo') if 'vehiculo' in request.POST else None
				chofer = request.POST.getlist('chofer') if 'chofer' in request.POST else None
				situacion = request.POST['situacion']			
				#CONFIG				 
				report = JasperReportBase()  
				report.report_name  = 'rpt_bascula008'
				report.report_url = reverse_lazy(report.report_name)
				report.report_title = Module.objects.filter(url=report.report_url).first().description                      
				#PARAMETROS
				report.params['P_TITULO2'] = self.request.user.sucursal.denominacion_puesto			
				report.params['P_TITULO3'] = 'INFORME DE TIEMPO TRANSCURRIDO DE VEHICULOS EN TRÁNSITO'				
				report.params['P_SUCURSAL_ID'] = ",".join(sucursal) if sucursal!=[''] else None
				report.params['P_TRANSPORTE_ID'] = ",".join(transporte) if transporte!=[''] else None
				report.params['P_CLIENTE_ID'] = ",".join(cliente) if cliente!=[''] else None
				report.params['P_DESTINO_ID'] = ",".join(destino) if destino!=[''] else None
				report.params['P_PRODUCTO_ID'] = ",".join(producto) if producto!=[''] else None
				report.params['P_VEHICULO_ID']= ",".join(vehiculo) if vehiculo!=[''] else None
				report.params['P_CHOFER_ID'] = ",".join(chofer) if chofer!=[''] else None
				report.params['P_SITUACION'] = situacion if len(situacion)!=0 else None
				report.params['P_FECHA_DESDE'] = fecha_desde
				report.params['P_FECHA_HASTA'] = fecha_hasta

				return report.render_to_response(tipo)

			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			print('####################### ERROR #######################')
			print(str(e))
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		suc_usuario = self.request.user.sucursal.id
		context = super().get_context_data(**kwargs)
		context['title'] = 'Reporte de Tiempo Transcurrido de Vehiculos en Tránsito'
		context['action'] = 'report'
		context['suc_usuario'] = suc_usuario
		return context