import json
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.bascula.forms import ClienteProducto, ClienteProductoForm
from core.security.mixins import PermissionMixin


class ClienteProductoList(PermissionMixin, ListView):
	model = ClienteProducto
	template_name = 'clienteproducto/list.html'
	permission_required = 'view_clienteproducto'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def post(self,request,*args,**kwargs):
		data ={}		
		try:
			action = request.POST['action']
			if action == 'search':
				data =[]
								
				search = ClienteProducto.objects.filter(sucursal=self.request.user.sucursal.id)
				for i in search:
					data.append(i.toJSON())
			else:	
				data['error']= 'No ha ingresado a ninguna opción'
		except Exception as e:
			data['error'] = str(e)
		# return JsonResponse(data,safe=False)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['create_url'] = reverse_lazy('clienteproducto_create')
		context['title'] = 'Listado de Clientes y sus Productos'
		return context


class ClienteProductoCreate(PermissionMixin, CreateView):
	model = ClienteProducto
	template_name = 'clienteproducto/create.html'
	form_class = ClienteProductoForm
	success_url = reverse_lazy('clienteproducto_list')
	permission_required = 'add_clienteproducto'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()            
			if type == 'denominacion':                
				if ClienteProducto.objects.filter(denominacion__iexact=obj):
					data['valid'] = False
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST['action']
		try:
			if action == 'add':
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
		context['title'] = 'Nuevo registro de un ClienteProducto'
		context['action'] = 'add'
		context['usu_sucursal'] = self.request.user.sucursal.id
		return context


class ClienteProductoUpdate(PermissionMixin, UpdateView):
	model = ClienteProducto
	template_name = 'clienteproducto/create.html'
	form_class = ClienteProductoForm
	success_url = reverse_lazy('clienteproducto_list')
	permission_required = 'change_clienteproducto'

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
				if ClienteProducto.objects.filter(denominacion__iexact=obj).exclude(id=id):
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
		context['title'] = 'Edición de Cliente Producto'
		context['action'] = 'edit'
		context['usu_sucursal'] = self.request.user.sucursal.id
		return context


class ClienteProductoDelete(PermissionMixin, DeleteView):
	model = ClienteProducto
	template_name = 'clienteproducto/delete.html'
	success_url = reverse_lazy('clienteproducto_list')
	permission_required = 'delete_clienteproducto'

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
