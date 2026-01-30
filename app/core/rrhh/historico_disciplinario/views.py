import json

from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, UpdateView

from core.base.views.generics import BaseListView
from core.rrhh.empleado.forms import EmpleadoFilterForm
from core.rrhh.historico_disciplinario.forms import HistoricoDisciplinarioForm

from core.rrhh.models import Empleado, HistoricoDisciplinario
from core.rrhh.empleado.views import EmpleadoScopedMixin
from core.security.mixins import PermissionMixin

class HistoricoDisciplinarioList(PermissionMixin,EmpleadoScopedMixin, BaseListView):
	# Modelo base y permiso requerido
	model = HistoricoDisciplinario
	context_prefix = "Histórico Disciplinario"
	create_url_name = "historico_disciplinario_create"
	permission_required = "view_historicodisciplinario"
	
	# Campos habilitados para búsqueda y ordenamiento
	search_fields = [
		"empleado__nombre",
		"empleado__apellido",
		"institucion__denominacion",
	]
	numeric_fields = ["id", "empleado_id"]
	default_order_fields = ["empleado__apellido", "empleado__nombre"]

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("historico_disciplinario_list")

	def get_template_names(self):
		# Usa plantilla distinta si es vista personal
		return ["historico_disciplinario/list_self.html"] if self.is_self_view else ["historico_disciplinario/list.html"]

	def get_queryset(self):
		# 1. Recuperamos el QuerySet base del Mixin (Seguridad de sucursal/usuario)
		qs = super().get_queryset()

		# 2. Capturamos el ID del empleado enviado por el buscador/combo
		empleado_id = self.request.POST.get("empleado")

		# 3. COMPORTAMIENTO ESPECÍFICO:
		# Solo filtramos y mostramos si se envía un empleado_id.
		# NOTA: En la vista personal (is_self_view), el Mixin ya hace el trabajo,
		# así que permitimos que pase sin el requisito del POST.
		if not self.is_self_view:
			if empleado_id:
				qs = qs.filter(empleado_id=empleado_id)
			else:
				# Si no hay empleado_id y no es vista personal, devolvemos vacío
				return self.model.objects.none()

		# 4. Optimización final si hay datos que mostrar
		return qs.select_related("empleado",)

	def post(self, request, *args, **kwargs):
		# Maneja acciones POST como búsqueda
		data = {}
		action = request.POST.get("action", "")
		try:
			if action == "search":
				data = self.handle_search(request)
			else:
				data["error"] = "No ha ingresado una opción válida"
		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(data, content_type="application/json")

	def get_context_data(self, **kwargs):
		# Agrega contexto adicional a la plantilla
		context = super().get_context_data(**kwargs)
		if self.is_self_view:
			context["create_url"] = reverse_lazy(self.create_url_name + "_self")
			# Enriquecer contexto con datos del empleado
			return self.enrich_context_with_empleado(context, prefijo=self.context_prefix)
		else:
			context["create_url"] = reverse_lazy(self.create_url_name)
			context["title"] = "Listado de " + self.context_prefix
			context["filter_form"] = EmpleadoFilterForm(self.request.GET or None, user=self.request.user)
		return context

class HistoricoDisciplinarioCreate(PermissionMixin,EmpleadoScopedMixin,CreateView):
	model = HistoricoDisciplinario
	form_class = HistoricoDisciplinarioForm
	template_name = "historico_disciplinario/create.html"
	#success_url se define en get_success_url
	permission_required = "add_historicodisciplinario" # ver comentario en PermissionMixin para más detalles

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("historico_disciplinario_list")
	
	def form_valid(self, form):
		form = self.asignar_empleado_a_form(form)
		return super().form_valid(form)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST.get("action", "")
		try:
			if action == "add":
				form = self.get_form()
				if form.is_valid():                                       
					form = self.asignar_empleado_a_form(form)
					form.save()				
				else:
					data["error"] = form.errors					
			elif action == "validate_data":
				return self.validate_data()
			else:
				data["error"] = "No ha seleccionado ninguna opción"
		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(json.dumps(data), content_type="application/json")

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context["list_url"] = self.get_success_url()
		context["action"] = "add"
		#Titulo con el nombre del empleado
		return self.enrich_context_with_empleado(context, prefijo="Agregar Histórico Disciplinario")

class HistoricoDisciplinarioUpdate(PermissionMixin,EmpleadoScopedMixin,UpdateView):
	model = HistoricoDisciplinario
	form_class = HistoricoDisciplinarioForm
	template_name = "historico_disciplinario/create.html"
	#success_url se define en get_success_url
	permission_required = "change_historicodisciplinario"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("historico_disciplinario_list")

	def get_object(self, queryset=None):
		try:
			if self.is_self_view:
				empleado = Empleado.objects.get(usuario=self.request.user)
				
				return HistoricoDisciplinario.objects.get(pk=self.kwargs["pk"], empleado=empleado)
			else:
				return HistoricoDisciplinario.objects.get(pk=self.kwargs["pk"])
		except (Empleado.DoesNotExist, HistoricoDisciplinario.DoesNotExist):
			raise Http404("No se encontró la formación académica.")

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST.get("action", "")
		try:
			if action == "edit":
				obj = self.get_object()
				form = self.form_class(request.POST, request.FILES, instance=obj)
				  
				# 🔧 Ajuste dinámico: si es self_view, quitamos el campo empleado del form
				if self.is_self_view and 'empleado' in form.fields:
					form.fields.pop('empleado')
				
				if form.is_valid():
					if self.is_self_view:
						try:
							empleado = Empleado.objects.get(usuario=request.user)
							form.instance.empleado = empleado
						except Empleado.DoesNotExist:
							data["error"] = "No se encontró un empleado vinculado al usuario actual"
							return JsonResponse(data, status=400)
					form.save()
				else:
					data["error"] = form.errors
			elif action == "validate_data":
				return self.validate_data()
			else:
				data["error"] = "No ha seleccionado ninguna opción"

		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(json.dumps(data), content_type="application/json")

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context["list_url"] = self.get_success_url()
		context["action"] = "edit"
		context["instance"] = self.object
		#Titulo con el nombre del empleado
		return self.enrich_context_with_empleado(context, prefijo="Modificar Histórico Disciplinario")

class HistoricoDisciplinarioDelete(EmpleadoScopedMixin, DeleteView):
	model = HistoricoDisciplinario
	template_name = "historico_disciplinario/delete.html"
	permission_required = "delete_historicodisciplinario"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("historico_disciplinario_list")

	def post(self, request, *args, **kwargs):
		data = {}
		try:
			self.get_object().delete()
		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(json.dumps(data), content_type="application/json")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["title"] = "Notificación de eliminación"
		context["list_url"] = self.get_success_url()
		return context