# Librerías estándar
import json
import json as simplejson
from datetime import datetime
from multiprocessing import context

# Librerías de terceros
from dateutil.relativedelta import relativedelta
from weasyprint import HTML

# Django
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, View

# Proyecto interno
from config import settings
from core.base.models import Barrio, Ciudad
from core.base.procedures import sp_identificaciones
from core.base.utils import YYYY_MM_DD, get_fecha_actual, isNULL
from core.base.views.generics import BaseListView
from core.rrhh.models import Empleado
from core.rrhh.empleado.forms import EmpleadoFilterForm, EmpleadoForm
from core.security.mixins import PermissionMixin
from core.user.models import User

# MSSQL
def get_datos_persona(request):
	# import pdb; pdb.set_trace()
	data = str(request.GET.get("ci", "X"))
	# print("*" * 10)
	# print(vCi)
	persona = sp_identificaciones(ci=data)
	# print(persona)
	return HttpResponse(simplejson.dumps(persona), content_type="application/json")

# Mixin institucional para vistas relacionadas al modelo Empleado
# Scoped (alcance) a un empleado específico (usuario actual)
class EmpleadoScopedMixin:
	"""
	Mixin institucional para vistas relacionadas al modelo Empleado.
	- Filtra objetos por usuario si es vista personal (_self)
	- Enriquecer contexto con datos del empleado
	- Genera títulos personalizados
	Requiere que el modelo tenga un campo 'empleado'.
	"""
	model = None  # debe ser definido en la vista 
	
	# Obtener empleado vinculado al usuario actual
	def get_empleado(self):
		"""Empleado vinculado al usuario actual"""
		return Empleado.objects.filter(usuario=self.request.user).first()
	
	# Obtener kwargs del formulario y agregar is_self_view flag si es 
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["is_self_view"] = getattr(self, "is_self_view", False)
		return kwargs
	
	# Detectar si es vista personal (_self)
	@property
	def is_self_view(self):
		"""Detecta si la vista es personal (_self)"""
		return self.request.resolver_match.url_name.endswith("_self")
	
	# Definir URL de éxito según tipo de vista
	def get_success_url_for(self, base_name):
		return reverse_lazy(f"{base_name}_self") if self.is_self_view else reverse_lazy(base_name)
	
	# Asignar empleado al formulario si es vista personal
	def asignar_empleado_a_form(self, form):
		"""
		Asigna el empleado al formulario antes de guardar.
		- Si es self_view: usa el empleado vinculado al request.user
		- Si es admin: deja el empleado seleccionado en el formulario
		Además imprime kwargs para trazabilidad.
		"""
		try:
			if getattr(self, "is_self_view", False):
				# Vista propia: asignar automáticamente el empleado del usuario logueado
				empleado = Empleado.objects.get(usuario=self.request.user)
				form.instance.empleado = empleado
				print("[asignar_empleado_a_form] Empleado asignado (self_view):", empleado)
			else:
				# Vista admin: ya viene del campo 'empleado' en el form
				if not form.instance.empleado_id:
					raise ValueError("Debe seleccionar un empleado.")
				print("[asignar_empleado_a_form] Empleado asignado (admin):", form.instance.empleado_id)
		except Exception as e:
			print(f"[asignar_empleado_a_form] Error: {e}")

		return form
	
	# Filtrar queryset por empleado si es vista personal
	def get_queryset(self):
		"""Filtra por empleado si es vista personal"""
		assert self.model is not None, "Debes definir 'model' en la vista"
		qs = self.model.objects.select_related("empleado")
		if self.is_self_view:
			empleado = self.get_empleado()
			return qs.filter(empleado=empleado) if empleado else self.model.objects.none()
		return qs
	
	# Generar título con nombre del empleado
	def get_titulo_empleado(self, prefijo="Datos"):
		"""Genera título personalizado con nombre del empleado según el modo de vista"""		
		if self.is_self_view:
			try:
				empleado = Empleado.objects.get(usuario=self.request.user)
			except Empleado.DoesNotExist:
				return f"{prefijo} (usuario sin empleado)"
		else:
			empleado = getattr(self.object, "empleado", None)
			if not empleado:
				return f"{prefijo} (sin empleado asociado)"

		return f"{prefijo} de {empleado.nombre} {empleado.apellido}"
	
	# Enriquecer contexto con datos del empleado
	def enrich_context_with_empleado(self, context, prefijo="Datos"):
		"""Agrega 'title', 'empleado' e indicador de modo al contexto"""
		
		if self.is_self_view:
			try:
				empleado = Empleado.objects.get(usuario=self.request.user)
			except Empleado.DoesNotExist:
				empleado = None
		else:
			empleado = getattr(self.object, "empleado", None)

		context["title"] = self.get_titulo_empleado(prefijo)
		context["empleado"] = empleado
		context["is_self"] = self.is_self_view  
		return context


class EmpleadoList(PermissionMixin,BaseListView):
	model = Empleado
	context_prefix = "Empleado"
	create_url_name = "empleado_create"
	template_name = "empleado/list.html"
	permission_required = "view_empleado"

	search_fields = ["ci", "nombre", "apellido"]
	numeric_fields = ["id", "ci"]
	default_order_fields = ["id"]

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST["action"]
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
		# Lista de empleados solo disponible en vista general para administradores
		context = super().get_context_data(**kwargs)	
		context["create_url"] = reverse_lazy(self.create_url_name)
		context["title"] = "Listado de " + self.context_prefix
		context["filter_form"] = EmpleadoFilterForm(self.request.GET or None)
		return context


# class EmpleadoCreate(PermissionMixin,CreateView):
class EmpleadoCreate(CreateView):
	model = Empleado
	template_name = "empleado/create.html"
	form_class = EmpleadoForm
	success_url = reverse_lazy("empleado_list")
	permission_required = "add_empleado"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {"valid": True}
		type = self.request.POST["type"]
		obj = self.request.POST["obj"].strip()
		print(type)
		print(obj)

		try:
			type = self.request.POST["type"]
			obj = self.request.POST["obj"].strip()
			if type == "ci":
				if Empleado.objects.filter(ci__iexact=obj):
					data["valid"] = False
			if type == "ruc":
				if Empleado.objects.filter(ruc__iexact=obj):
					data["valid"] = False
			if type == "fec_nacimiento":
				fec_nacimiento = datetime.strptime(
					obj, "%d/%m/%Y"
				)  # Este del from datetime
				edad = relativedelta(get_fecha_actual, fec_nacimiento)
				if edad.years:
					if abs(edad.years) < 18:
						data["valid"] = False
				else:
					data["valid"] = False
		except Exception as e:
			print(str(e))
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST["action"]
		try:
			if action == "add":
				with transaction.atomic():
					# Buscar usuario por DNI
					usuario = User.objects.filter(dni=request.POST['ci']).first()

					if usuario:
						# 🔄 Actualizar datos existentes
						usuario.first_name = request.POST['nombre']
						usuario.last_name = request.POST['apellido']
						usuario.email = request.POST['email']
						usuario.sucursal_id = 1
						if 'image' in request.FILES:
							usuario.image = request.FILES['image']
						usuario.create_or_update_password(request.POST['ci'])  # si aplica
						usuario.save()
						print(f"✅ Usuario actualizado: DNI {usuario.dni}")
					else:
						# 🆕 Crear nuevo usuario
						usuario = User()
						usuario.dni = request.POST['ci']
						usuario.username = usuario.dni
						usuario.first_name = request.POST['nombre']
						usuario.last_name = request.POST['apellido']
						usuario.email = request.POST['email']
						usuario.sucursal_id = 1
						if 'image' in request.FILES:
							usuario.image = request.FILES['image']
						usuario.create_or_update_password(usuario.dni)
						usuario.save()
						print(f"✅ Usuario creado: DNI {usuario.dni}")

					# Asignar grupo
					group = Group.objects.get(pk=settings.GROUPS.get('empleado'))
					usuario.groups.add(group)
								   
					
					#INSTANCIAR EMPLEADO
					empleado = Empleado()
					empleado.usuario = usuario
					empleado.ci = isNULL(request.POST["ci"])
					empleado.ruc = isNULL(request.POST["ruc"])
					empleado.nombre = isNULL(request.POST["nombre"])
					empleado.apellido = isNULL(request.POST["apellido"])
					empleado.nacionalidad_id = isNULL(request.POST["nacionalidad"])
					empleado.ciudad_id = isNULL(request.POST["ciudad"])
					empleado.barrio_id = isNULL(request.POST["barrio"])
					empleado.direccion = isNULL(request.POST["direccion"])
					empleado.celular = isNULL(request.POST["celular"])
					empleado.telefono = isNULL(request.POST["telefono"])
					empleado.email = isNULL(request.POST["email"])
					empleado.fec_nacimiento = YYYY_MM_DD(isNULL(request.POST["fec_nacimiento"]))
					empleado.sexo_id = isNULL(request.POST["sexo"])
					empleado.estado_civil_id = isNULL(request.POST["estado_civil"])                   
					empleado.save()
					data["id"] = empleado.id

				# data = self.get_form().save()
			elif action == "validate_data":
				return self.validate_data()
			elif action == "search_ciudad":
				data = []
				term = request.POST["term"]
				qs = Ciudad.objects.filter(
					Q(activo__exact=True)
					& (
						Q(distrito__denominacion__icontains=term)
						| Q(denominacion__icontains=term)
					)
				).order_by("denominacion", "distrito_id")[0:25]

				data = [{"id": "", "text": "------------"}]
				id_dpto_aux = 0
				for i in qs:
					if id_dpto_aux != i.distrito_id:
						data.append(
							{
								"text": str(i.distrito),
								"children": [{"id": i.id, "text": str(i)}],
							}
						)
					else:
						data.append(
							{
								"children": [{"id": i.id, "text": str(i)}],
							}
						)
					id_dpto_aux = i.distrito_id

			elif action == "search_barrio":
				data = [{"id": "", "text": "---------"}]
				ciudad_list = None
				if "id" in request.POST:
					ciudad_list = [request.POST["id"] if "id" in request.POST else None]

				elif "id[]" in request.POST:
					ciudad_list = (
						request.POST.getlist("id[]") if "id[]" in request.POST else None
					)
				if ciudad_list:
					for i in Barrio.objects.filter(ciudad_id__in=ciudad_list):
						data.append(
							{"id": i.id, "text": str(i), "data": i.ciudad.toJSON()}
						)
			else:
				data["error"] = "No ha seleccionado ninguna opción"
		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(json.dumps(data), content_type="application/json")

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context["list_url"] = self.success_url
		context["title"] = "Nuevo registro de un Empleado"
		context["action"] = "add"
		context["instance"] = None
		return context

class EmpleadoUpdate(PermissionMixin, EmpleadoScopedMixin, UpdateView):
	model = Empleado
	form_class = EmpleadoForm
	template_name = "empleado/create.html"
	permission_required = "change_empleado"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.is_self = self.request.resolver_match.url_name.endswith("_self")
		self.object = self.get_object()
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		if self.is_self:
			return reverse_lazy("dashboard")  # o "empleado_perfil_self"
		return reverse_lazy("empleado_list")

	def get_object(self, queryset=None):
		try:
			if self.is_self:
				return Empleado.objects.get(usuario=self.request.user)
			return Empleado.objects.get(pk=self.kwargs["pk"])
		except Empleado.DoesNotExist:
			raise Http404("No se encontró el perfil del empleado.")

	def validate_data(self):
		data = {"valid": True}
		try:
			tipo = self.request.POST.get("type")
			obj = self.request.POST.get("obj", "").strip()
			id = self.get_object().id
			if tipo == "ci":
				if Empleado.objects.filter(ci__iexact=obj).exclude(id=id).exists():
					data["valid"] = False
			elif tipo == "ruc":
				if Empleado.objects.filter(ruc__iexact=obj).exclude(id=id).exists():
					data["valid"] = False
		except Exception:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST.get("action", "")
		try:
			if action == "edit":
				form = self.get_form()
				if form.is_valid():

					empleado = form.save(commit=False)
					usuario = empleado.usuario

					usuario.first_name = request.POST.get("nombre", "").strip()
					usuario.last_name = request.POST.get("apellido", "").strip()
					usuario.dni = request.POST.get("ci", "").strip()
					usuario.username = usuario.dni
					usuario.email = request.POST.get("email", "").strip()

					if "image-clear" in request.POST and usuario.image:
						usuario.image.delete(save=False)
						usuario.image = None
					if "image" in request.FILES:
						usuario.image = request.FILES["image"]

					usuario.save()

					group = Group.objects.get(pk=settings.GROUPS.get("empleado"))
					usuario.groups.add(group)

					empleado.ci = isNULL(request.POST.get("ci"))
					empleado.ruc = isNULL(request.POST.get("ruc"))
					empleado.nombre = isNULL(request.POST.get("nombre"))
					empleado.apellido = isNULL(request.POST.get("apellido"))
					empleado.nacionalidad_id = isNULL(request.POST.get("nacionalidad"))
					empleado.ciudad_id = isNULL(request.POST.get("ciudad"))
					empleado.barrio_id = isNULL(request.POST.get("barrio"))
					empleado.direccion = isNULL(request.POST.get("direccion"))
					empleado.celular = isNULL(request.POST.get("celular"))
					empleado.telefono = isNULL(request.POST.get("telefono"))
					empleado.email = isNULL(request.POST.get("email"))
					empleado.fec_nacimiento = YYYY_MM_DD(isNULL(request.POST.get("fec_nacimiento")))
					empleado.sexo_id = isNULL(request.POST.get("sexo"))
					empleado.estado_civil_id = isNULL(request.POST.get("estado_civil"))

					empleado.save()
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
		context = super().get_context_data(**kwargs)
		context["list_url"] = self.get_success_url()
		context["action"] = "edit"
		context["instance"] = self.object
		return self.enrich_context_with_empleado(context, prefijo="Editar Perfil")

class EmpleadoDelete(PermissionMixin, DeleteView):
	model = Empleado
	template_name = "empleado/delete.html"
	success_url = reverse_lazy("empleado_list")
	permission_required = "delete_empleado"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

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
		context["list_url"] = self.success_url
		return context


class EmpleadoUpdatePerfil(PermissionMixin,UpdateView):
	# class EmpleadoUpdatePerfil(PermissionMixin, UpdateView):
	model = Empleado
	form_class = EmpleadoForm
	template_name = "empleado/create.html"
	success_url = reverse_lazy("dashboard")
	permission_required = "change_empleado"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		# self.object = self.get_object()
		return super().dispatch(request, *args, **kwargs)
	
	# # Sobrescribir get_success_url para redirigir a la misma página
	# def get_success_url(self):
	#     return self.request.path

	# Obtener empleado asociado al usuario logueado
	def get_empleado(self):
		try:
			return Empleado.objects.get(usuario=self.request.user)
		except Empleado.DoesNotExist:
			raise Http404("No se encontró el perfil del empleado asociado al usuario.")

	# Sobrescribir get_object para obtener el empleado del usuario logueado
	def get_object(self, queryset=None):
		empleado = self.get_empleado()
		if empleado:
			return empleado
		return Empleado()
	
	# Validar datos únicos
	def validate_data(self):
		data = {"valid": True}
		try:
			type = self.request.POST["type"]
			obj = self.request.POST["obj"].strip()
			id = self.get_object().id
			if type == "ci":
				if Empleado.objects.filter(ci__iexact=obj).exclude(id=id):
					data["valid"] = False
			if type == "ruc":
				if Empleado.objects.filter(ruc__iexact=obj).exclude(id=id):
					data["valid"] = False
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST.get("action")
		try:
			if action == "edit":
				with transaction.atomic():
					empleado = self.get_object()
					usuario = empleado.usuario

					# Actualizar datos del usuario
					usuario.first_name = request.POST.get("nombre", "").strip()
					usuario.last_name = request.POST.get("apellido", "").strip()
					usuario.dni = request.POST.get("ci", "").strip()
					usuario.username = usuario.dni
					usuario.email = request.POST.get("email", "").strip()

					# Manejo de imagen
					if "image-clear" in request.POST:
						if usuario.image:
							usuario.image.delete(save=False)
						usuario.image = None
					if "image" in request.FILES:
						usuario.image = request.FILES["image"]

					usuario.save()

					# Asignar grupo si no está
					group = Group.objects.get(pk=settings.GROUPS.get("empleado"))
					usuario.groups.add(group)

					# Actualizar datos del empleado
					empleado.ci = isNULL(request.POST.get("ci"))
					empleado.ruc = isNULL(request.POST.get("ruc"))
					empleado.nombre = isNULL(request.POST.get("nombre"))
					empleado.apellido = isNULL(request.POST.get("apellido"))
					empleado.nacionalidad_id = isNULL(request.POST.get("nacionalidad"))
					empleado.ciudad_id = isNULL(request.POST.get("ciudad"))
					empleado.barrio_id = isNULL(request.POST.get("barrio"))
					empleado.direccion = isNULL(request.POST.get("direccion"))
					empleado.celular = isNULL(request.POST.get("celular"))
					empleado.telefono = isNULL(request.POST.get("telefono"))
					empleado.email = isNULL(request.POST.get("email"))
					empleado.fec_nacimiento = YYYY_MM_DD(isNULL(request.POST.get("fec_nacimiento")))
					empleado.sexo_id = isNULL(request.POST.get("sexo"))
					empleado.estado_civil_id = isNULL(request.POST.get("estado_civil"))
					empleado.save()

					data["id"] = empleado.id

			elif action == "validate_data":
				return self.validate_data()
			else:
				data["error"] = "No ha seleccionado ninguna opción"
		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(json.dumps(data), content_type="application/json")


	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context["list_url"] = self.success_url
		context["title"] = f" Perfil de {self.object.nombre} {self.object.apellido}"
		context["action"] = "edit"
		context["instance"] = self.object
		return context


class CVEmpleadoPDFView(View):
	template_name = 'empleado/cv_empleado_pdf.html'

	def get_empleado(self, pk):
		try:
			return Empleado.objects.select_related(
				'nacionalidad', 'ciudad', 'barrio', 'sexo', 'estado_civil'
			).get(pk=pk)
		except Empleado.DoesNotExist:
			raise Http404("No se encontró el empleado.")

	def get(self, request, pk):
		empleado = self.get_empleado(pk)
		context = {
			'empleado': empleado,
			'usuario': empleado.usuario,
			'fecha_generacion': request.timestamp if hasattr(request, 'timestamp') else None,
		}
		html_string = render_to_string(self.template_name, context)
		pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="cv_{empleado.nombre}_{empleado.apellido}.pdf"'
		return response

