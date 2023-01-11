import json
import math
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.bascula.forms import Chofer, ChoferForm
from core.security.mixins import PermissionMixin


class ChoferList(PermissionMixin, ListView):
	model = Chofer
	template_name = 'chofer/list.html'
	permission_required = 'view_chofer'

	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		data = {}
		# print(request.POST)
		action = request.POST['action']

		try:
			if action =='search':
				data=[]
									
				_start = request.POST['start']
				_length = request.POST['length']
				_search = request.POST['search[value]']								
				
				_order = []
	
			
				for i in range(9): 
					_column_order = f'order[{i}][column]'
					# print('Column Order:',_column_order)
					if _column_order in request.POST:					
						_column_number = request.POST[_column_order]								
						_order.append(request.POST[f'columns[{_column_number}][data]'].split(".")[0])
					if f'order[{i}][dir]' in request.POST:
						_dir = request.POST[f'order[{i}][dir]']
						if (_dir=='desc'):
							_order[i] = f"-{_order[i]}"
			
				_where = "'' = %s"				
				if len(_search):
					if _search.isnumeric():
						_where = " codigo = %s"				
					else:
						_search = "%" + _search.replace(' ', '%') + "%"
						_where = " upper(codigo ||' '|| nombre ||' '|| apellido ) LIKE upper(%s)"
					
				print(_where)
				qs = Chofer.objects\
								.filter()\
								.extra(where=[_where], params=[_search])\
								.order_by(*_order)
								   
				total = qs.count()
				print(total)
				
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
					# item['position'] = position					
					data.append(item)
					position += 1
				# print(data)
				data = {'data': data,
						'page': page,  # [opcional]
						'per_page': per_page,  # [opcional]
						'recordsTotal': total,
						'recordsFiltered': total, }
			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['create_url'] = reverse_lazy('chofer_create')
		context['title'] = 'Listado de Choferes'
		return context


class ChoferCreate(PermissionMixin, CreateView):
	model = Chofer
	template_name = 'chofer/create.html'
	form_class = ChoferForm
	success_url = reverse_lazy('chofer_list')
	permission_required = 'add_chofer'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()            
			if type == 'denominacion':                
				if Chofer.objects.filter(denominacion__iexact=obj):
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
		context['title'] = 'Nuevo registro de un Chofer'
		context['action'] = 'add'
		return context


class ChoferUpdate(PermissionMixin, UpdateView):
	model = Chofer
	template_name = 'chofer/create.html'
	form_class = ChoferForm
	success_url = reverse_lazy('chofer_list')
	permission_required = 'change_chofer'

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
		context['title'] = 'Edición de un Chofer'
		context['action'] = 'edit'
		return context


class ChoferDelete(PermissionMixin, DeleteView):
	model = Chofer
	template_name = 'chofer/delete.html'
	success_url = reverse_lazy('chofer_list')
	permission_required = 'delete_chofer'

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
