import json
from datetime import datetime
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, UpdateView

from core.base.views.generics import BaseListView
from core.rrhh.empleado.forms import EmpleadoFilterForm
from core.rrhh.documento_complementario.forms import DocumentoComplementarioFilterForm, DocumentoComplementarioForm

from core.rrhh.models import Empleado, DocumentoComplementario
from core.rrhh.empleado.views import EmpleadoScopedMixin
from core.security.mixins import PermissionMixin

class DocumentoComplementarioList(PermissionMixin,EmpleadoScopedMixin, BaseListView):
	# Modelo base y permiso requerido
	model = DocumentoComplementario
	context_prefix = "Documentos Complementarios"
	create_url_name = "documento_complementario_create"
	permission_required = "view_documentocomplementario"
	template_name = "documento_complementario/list.html"
	
	# Campos habilitados para búsqueda y ordenamiento
	search_fields = [
		"empleado__nombre",
		"empleado__apellido",
	]
	numeric_fields = ["id", "empleado_id"]
	default_order_fields = ["empleado__apellido", "empleado__nombre"]

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("documento_complementario_list")

	# def get_queryset(self):
	# 	# 1. Recuperamos el QuerySet base del Mixin (Seguridad de sucursal/usuario)
	# 	qs = super().get_queryset()

	# 	# 2. Capturamos el ID del empleado enviado por el buscador/combo
	# 	empleado_id = self.request.POST.get("empleado")

	# 	# 3. COMPORTAMIENTO ESPECÍFICO:
	# 	# Solo filtramos y mostramos si se envía un empleado_id.
	# 	# NOTA: En la vista personal (is_self_view), el Mixin ya hace el trabajo,
	# 	# así que permitimos que pase sin el requisito del POST.
	# 	if not self.is_self_view:
	# 		if empleado_id:
	# 			qs = qs.filter(empleado_id=empleado_id)
	# 		else:
	# 			# Si no hay empleado_id y no es vista personal, devolvemos vacío
	# 			return self.model.objects.none()

	# 	# 4. Optimización final si hay datos que mostrar
	# 	return qs.select_related("empleado", )

	

	def get_queryset(self):
		# 1. Recuperamos el QuerySet base (Seguridad de sucursal/usuario definida en su Mixin)
		qs = super().get_queryset()

		# 2. Capturamos los parámetros enviados por POST desde el DataTable
		empleado_id = self.request.POST.get("empleado")
		tipo_doc_id = self.request.POST.get("tipo_documento")
		rango_fecha = self.request.POST.get("rango_fecha")

		print(f"Filtros -> Emp: {empleado_id}, Tipo: {tipo_doc_id}, Rango: {rango_fecha}")

		if not self.is_self_view:
			if not any([empleado_id, tipo_doc_id, rango_fecha]):
				print("INFO: No hay filtros, retornando vacío")
				return self.model.objects.none()

		# 3. Lógica de Validación de Filtros
		# Si no es la vista personal (is_self_view), exigimos que exista al menos un filtro.
		if not getattr(self, 'is_self_view', False):
			# Verificamos si todos los campos están vacíos
			if not any([empleado_id, tipo_doc_id, rango_fecha]):
				return self.model.objects.none()

		# 4. Aplicación de Filtros Dinámicos
		
		# Filtro por Empleado (Opcional si hay otros filtros presentes)
		if empleado_id:
			qs = qs.filter(empleado_id=empleado_id)

		# Filtro por Tipo de Documento
		if tipo_doc_id:
			qs = qs.filter(tipo_documento_id=tipo_doc_id)

		# Filtro por Rango de Fechas (Procesamiento del string de Flatpickr)
		if rango_fecha and " a " in rango_fecha:
			try:
				# Separamos el string: "dd/mm/yyyy a dd/mm/yyyy"
				partes = rango_fecha.split(" a ")
				if len(partes) == 2:
					# .strip() elimina espacios accidentales
					f_desde_str = partes[0].strip()
					f_hasta_str = partes[1].strip()
					
					# Conversión a objetos date de Python
					f_desde = datetime.strptime(f_desde_str, '%d/%m/%Y').date()
					f_hasta = datetime.strptime(f_hasta_str, '%d/%m/%Y').date()
					
					# Aplicamos el filtro al campo fecha_documento
					# Usamos __range por si el campo en la DB es DateTimeField
					qs = qs.filter(fecha_documento__range=[f_desde, f_hasta])
			except (ValueError, TypeError, IndexError):
				# Si el formato de fecha es inválido, ignoramos el filtro de fecha
				pass

		# 5. Optimización de base de datos (Eager Loading)
		# Traemos las relaciones de una sola vez para evitar el problema N+1
		return qs.select_related("empleado", "tipo_documento").order_by('-fecha_documento')

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
			context["empleado_filter_form"] = EmpleadoFilterForm(self.request.GET or None, user=self.request.user)
			context["documento_complementario_filter_form"] = DocumentoComplementarioFilterForm(self.request.GET or None)
		return context

class DocumentoComplementarioCreate(PermissionMixin,EmpleadoScopedMixin,CreateView):
	model = DocumentoComplementario
	form_class = DocumentoComplementarioForm
	template_name = "documento_complementario/create.html"
	#success_url se define en get_success_url
	permission_required = "add_documentocomplementario" # ver comentario en PermissionMixin para más detalles

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("documento_complementario_list")
	
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
		return self.enrich_context_with_empleado(context, prefijo="Agregar Documentos Complementarios")

class DocumentoComplementarioUpdate(PermissionMixin,EmpleadoScopedMixin,UpdateView):
	model = DocumentoComplementario
	form_class = DocumentoComplementarioForm
	template_name = "documento_complementario/create.html"
	#success_url se define en get_success_url
	permission_required = "change_documentocomplementario"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("documento_complementario_list")

	def get_object(self, queryset=None):
		try:
			if self.is_self_view:
				empleado = Empleado.objects.get(usuario=self.request.user)
				
				return DocumentoComplementario.objects.get(pk=self.kwargs["pk"], empleado=empleado)
			else:
				return DocumentoComplementario.objects.get(pk=self.kwargs["pk"])
		except (Empleado.DoesNotExist, DocumentoComplementario.DoesNotExist):
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
		return self.enrich_context_with_empleado(context, prefijo="Modificar Documentos Complementarios")

class DocumentoComplementarioDelete(PermissionMixin,EmpleadoScopedMixin, DeleteView):
	model = DocumentoComplementario
	template_name = "documento_complementario/delete.html"
	permission_required = "delete_documentocomplementario"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def get_success_url(self):
		return self.get_success_url_for("documento_complementario_list")

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


