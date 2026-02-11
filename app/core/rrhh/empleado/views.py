# Librerías estándar
import json
import json as simplejson
from datetime import datetime
from datetime import date, datetime
from urllib import request
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
from django.views.generic import CreateView, DeleteView, UpdateView,  View

# Proyecto interno
from config import settings
from core.base.models import Barrio, Ciudad, RefDet
from core.base.procedures import sp_identificaciones
from core.base.utils import  get_fecha_actual, get_fecha_actual_ymd, isNULL, validar_mayor_edad
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

	def get_queryset(self):
		assert self.model is not None, "Debes definir 'model' en la vista"
		
		usuario = self.request.user
		qs = self.model.objects.all()

		print(f"\n--- ANALIZANDO ACCESO PARA: {usuario.username} ---")

		# 1. CASO VISTA PERSONAL (_self)
		if self.is_self_view:
			empleado = self.get_empleado()
			print(f"Ruta tomada: VISTA PERSONAL. Empleado: {empleado}")
			return qs.filter(empleado=empleado) if empleado else self.model.objects.none()

		# 2. CASO ADMIN GLOBAL O SUPERUSER
		# Verifica si el usuario tiene el flag is_superuser o pertenece al grupo global
		es_global = usuario.groups.filter(name='ADMIN_RRHH_GLOBAL').exists()
		
		if usuario.is_superuser or es_global:
			print(f"Ruta tomada: ADMIN GLOBAL. (Superuser: {usuario.is_superuser}, Grupo Global: {es_global})")
			print("RESULTADO: No se aplica filtro de sucursal.")
			return qs.select_related("empleado") if hasattr(self.model, 'empleado') else qs

		# 3. CASO ADMIN DE SUCURSAL
		try:
			# IMPORTANTE: Usamos .select_related('sucursal') para el print
			empleado_admin = usuario.empleado 
			sucursal_id = empleado_admin.sucursal_id
			print(f"Ruta tomada: ADMIN SUCURSAL. Sucursal ID detectado: {sucursal_id}")

			if self.model == Empleado:
				qs_final = qs.filter(sucursal_id=sucursal_id)
			else:
				# Aquí está el filtro clave para ExperienciaLaboral, Capacitacion, etc.
				qs_final = qs.filter(empleado__sucursal_id=sucursal_id)
			
			print(f"Filtro aplicado: empleado__sucursal_id = {sucursal_id}")
			print(f"Registros finales en QuerySet: {qs_final.count()}")
			return qs_final.select_related("empleado")
			
		except Exception as e:
			print(f"Ruta tomada: ERROR/DESCONOCIDO. Detalle: {str(e)}")
			return self.model.objects.none()
	
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
	numeric_fields = ["id", "ci","legajo"]
	default_order_fields = ["id"]

	# def get_queryset(self):
	# 	# Usamos el manager personalizado que creamos antes
	# 	# Esto garantiza que el Admin Global vea todo y el de Sucursal solo lo suyo
	# 	return Empleado.objects.para_usuario(self.request.user)
	def get_queryset(self):
		# 1. Recuperamos el QuerySet base (Seguridad de usuario/sucursal)
		qs = super().get_queryset()

		# 2. Capturamos los datos del POST
		sucursal_id = self.request.POST.get("sucursal")
		empleado_id = self.request.POST.get("empleado")

		# 3. FILTRO OBLIGATORIO: Sucursal
		# Si viene en el POST, filtramos. Si no, podrías usar la sucursal del usuario
		if sucursal_id:
			qs = qs.filter(sucursal_id=sucursal_id)
		
		# 4. FILTRO OPCIONAL: Empleado	
		# Si el usuario seleccionó un empleado específico, filtramos
		if empleado_id:
			qs = qs.filter(id=empleado_id)
			
			# SI empleado_id es vacío, no agregamos más filtros (mostramos todos los de la sucursal)
			# Eliminamos el 'return objects.none()' anterior para permitir ver "todos"
		
		# NOTA: Si es 'is_self_view', el EmpleadoScopedMixin ya filtró por el ID del usuario actual.

		# 5. Optimización final
		return qs.select_related(
			"sucursal",      # Obligatorio para tu filtro por sucursal
			"usuario",       # Para verificar permisos o perfiles
			"nacionalidad",  # Evita consultas extra al mostrar el país
			"ciudad",        # Evita consultas extra al mostrar la ciudad
			"sexo",          # Tabla RefDet
			"estado_civil",  # Tabla RefDet
		)

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST["action"]
		try:
			if action == "search":
				data = self.handle_search(request)
				pass
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
		context["empleado_filter_form"] = EmpleadoFilterForm(self.request.GET or None, user=self.request.user)
		return context
		
# class EmpleadoCreate(PermissionMixin,CreateView):
class EmpleadoCreate(PermissionMixin,CreateView):
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
		# print(type)
		# print(obj)

		try:
			type = self.request.POST["type"]
			obj = self.request.POST["obj"].strip()			
			if type == "ci":
				if Empleado.objects.filter(ci__iexact=obj):
					data["valid"] = False
			if type == "ruc":
				if Empleado.objects.filter(ruc__iexact=obj):
					data["valid"] = False
			if type == "fecha_nacimiento":
				data["valid"] = validar_mayor_edad(obj)

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
					# Obtener datos del formulario
					activo = True if "on" in request.POST['activo'] else False

					ci = isNULL(request.POST["ci"])
					ruc = isNULL(request.POST["ruc"])
					nombre = isNULL(request.POST["nombre"])
					apellido = isNULL(request.POST["apellido"])
					sucursal_id = isNULL(request.POST["sucursal"])
					nacionalidad_id = isNULL(request.POST["nacionalidad"])
					ciudad_id = isNULL(request.POST["ciudad"])
					barrio_id = isNULL(request.POST["barrio"])
					direccion = isNULL(request.POST["direccion"])
					celular = isNULL(request.POST["celular"])
					telefono = isNULL(request.POST["telefono"])
					email = isNULL(request.POST["email"])
					fecha_nacimiento = isNULL(request.POST["fecha_nacimiento"])
					sexo_id = isNULL(request.POST["sexo"])
					estado_civil_id = isNULL(request.POST["estado_civil"])
					tipo_sanguineo_id = isNULL(request.POST["tipo_sanguineo"])
					fecha_vencimiento_ci = isNULL(request.POST["fecha_vencimiento_ci"])	
					archivo_pdf_ci = request.FILES.get("archivo_pdf_ci")
					fecha_ingreso = isNULL(request.POST["fecha_ingreso"])
					archivo_pdf_ingreso = request.FILES.get("archivo_pdf_ingreso")
					fecha_egreso = isNULL(request.POST["fecha_egreso"])
					archivo_pdf_egreso = request.FILES.get("archivo_pdf_egreso")
					
					if usuario:
						# 🔄 Actualizar datos existentes
						usuario.activo 		= activo
						usuario.first_name 	= nombre
						usuario.last_name 	= apellido
						usuario.email 		= email
						usuario.sucursal_id = sucursal_id
						if 'image' in request.FILES:
							usuario.image = request.FILES['image']
						usuario.create_or_update_password(ci)  # si aplica
						usuario.save()
						print(f"✅ Usuario actualizado: DNI {usuario.dni}")
					else:
						# 🆕 Crear nuevo usuario
						usuario = User()
						usuario.activo 		= activo
						usuario.dni 		= ci
						usuario.username 	= usuario.dni
						usuario.first_name 	= nombre
						usuario.last_name 	= apellido
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
					empleado.activo 	    		= activo
					empleado.sucursal_id 			= sucursal_id
					empleado.usuario 		 		= usuario
					empleado.ci 			 		= ci
					empleado.ruc 			 		= ruc
					empleado.nombre 		 		= nombre
					empleado.apellido 		 		= apellido
					empleado.nacionalidad_id 		= nacionalidad_id
					empleado.ciudad_id 		 		= ciudad_id
					empleado.barrio_id 		 		= barrio_id
					empleado.direccion 		 		= direccion
					empleado.celular 		 		= celular
					empleado.telefono 		 		= telefono
					empleado.email 			 		= email
					empleado.fecha_nacimiento  		= fecha_nacimiento
					empleado.sexo_id 		 		= sexo_id
					empleado.estado_civil_id		= estado_civil_id
					empleado.tipo_sanguineo_id		= tipo_sanguineo_id
					empleado.fecha_vencimiento_ci 	= fecha_vencimiento_ci
					empleado.fecha_ingreso 			= fecha_ingreso
					empleado.fecha_egreso 			= fecha_egreso

					if archivo_pdf_ci:
						# Si ya existía un archivo antes, lo borramos del disco
						if empleado.archivo_pdf_ci:
							empleado.archivo_pdf_ci.delete(save=False)
						# Asignamos el nuevo
						empleado.archivo_pdf_ci = archivo_pdf_ci     

					if archivo_pdf_ingreso:
						if empleado.archivo_pdf_ingreso:
							empleado.archivo_pdf_ingreso.delete(save=False)
						empleado.archivo_pdf_ingreso = archivo_pdf_ingreso
					
					if archivo_pdf_egreso:
						if empleado.archivo_pdf_egreso:
							empleado.archivo_pdf_egreso.delete(save=False)
						empleado.archivo_pdf_egreso = archivo_pdf_egreso	

					empleado.save()
					data["id"] 					= empleado.id

				# data = self.get_form().save()
			elif action == "validate_data":
				return self.validate_data()
		
			elif action == "search_empleado":
				# 1. Capturar el ID de sucursal (usando el nombre enviado por JS: sucursal_id)
				sucursal_id = request.POST.get("sucursal_id")
				print(f"[search_empleado] Sucursal ID recibida: {sucursal_id}")
				# 2. Filtrar el QuerySet inicial por sucursal si existe
				if sucursal_id and sucursal_id.isdigit():
					empleado_qs = Empleado.objects.filter(sucursal_id=sucursal_id, activo=True)
				else:
					# Si no hay sucursal (Admin Global), partimos de todos los activos
					empleado_qs = Empleado.objects.filter(activo=True)
				
				# 3. Capturar el término de búsqueda
				term = request.POST.get("term", "")
				
				# 4. Usar tu manager 'search' sobre el queryset ya filtrado por sucursal
				# Nota: Asegúrate de que tu manager acepte el parámetro request.user si lo usas para seguridad
				empleados = empleado_qs.search(term,request.user)
				print(f"[search_empleado] Término de búsqueda: '{term}' - Resultados encontrados: {empleados.count()}")
				# 5. Formatear para Select2 (Limitamos a 15 para velocidad)
				data = [{"id": emp.id, "text": emp.nombre_apellido_legajo} for emp in empleados]

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
		context = super().get_context_data(**kwargs)
		context["list_url"] = self.success_url
		context["title"] = "Nuevo registro de un Empleado"
		context["action"] = "add"
		context["instance"] = None
		return context
	
import json
from django.db import transaction
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.contrib.auth.models import Group
from django.conf import settings

# Importa tus utilidades y modelos
# from apps.rh.models import Empleado
# from apps.core.functions import isNULL, validar_mayor_edad

class EmpleadoUpdate(PermissionMixin, UpdateView):
	model = Empleado
	form_class = EmpleadoForm
	template_name = "empleado/create.html"

	# 1. Permisos dinámicos basados en la ruta
	def get_permission_required(self):
		if self.request.resolver_match.url_name.endswith("_self"):
			return ("change_empleado_self",)
		return ("change_empleado",)

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		# Identificar si es edición de perfil propio
		self.is_self = self.request.resolver_match.url_name.endswith("_self")
		
		# Seguridad: Si es 'self' pero el usuario no tiene perfil de empleado
		if self.is_self and not hasattr(request.user, 'empleado'):
			raise Http404("No tiene un perfil de empleado asociado a su cuenta de usuario.")
			
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		return reverse_lazy("dashboard") if self.is_self else reverse_lazy("empleado_list")

	# 2. Obtener el objeto correcto (El suyo o el de la PK)
	def get_object(self, queryset=None):
		try:
			if self.is_self:
				return self.request.user.empleado
			return Empleado.objects.get(pk=self.kwargs.get("pk"))
		except Empleado.DoesNotExist:
			raise Http404("El empleado solicitado no existe.")

	# 3. Consulta de campos bloqueados desde la DB (RefDet)
	def get_bloqueados_db(self):
		try:
			# Obtenemos el registro
			referencia = RefDet.objects.filter(cod_referencia='CAMPOS_BLOQUEADOS_EMPLEADO').first()
			
			if referencia and referencia.comentarios:
				# 1. Tomamos el string: "'ci', 'activo', 'sucursal'"
				# 2. Reemplazamos las comillas simples por nada
				# 3. Separamos por la coma
				# 4. Limpiamos espacios en blanco con strip()
				bloqueados = [
					item.strip().replace("'", "").replace('"', "") 
					for item in referencia.comentarios.split(',')
				]
				return bloqueados
				
			return []
		except Exception as e:
			print(f"Error en get_bloqueados_db: {e}")
			# Retornamos lista de seguridad en caso de error de DB
			return ['ci', 'activo', 'sucursal', 'fecha_ingreso', 'fecha_egreso', 'archivo_pdf_ingreso', 'archivo_pdf_egreso']
		
	# 4. Bloqueo visual de campos en el Formulario
	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		if self.is_self:
			# Campos que el empleado NO debe tocar (aunque use F12, el post está protegido)
			# TRAEMOS LOS CAMPOS DESDE LA DB
			bloqueados = self.get_bloqueados_db()
			for field in bloqueados:
				if field in form.fields:
					form.fields[field].disabled = True
					form.fields[field].widget.attrs['class'] = 'form-control bg-light'
		return form

	# 5. Validación remota (AJAX)
	def validate_data(self):
		data = {"valid": True}
		try:
			type_val = self.request.POST.get("type")
			obj_val = self.request.POST.get("obj", "").strip()
			id_actual = self.get_object().id
			
			if type_val == "ci":
				if Empleado.objects.filter(ci__iexact=obj_val).exclude(id=id_actual).exists():
					data["valid"] = False
			elif type_val == "ruc":
				if Empleado.objects.filter(ruc__iexact=obj_val).exclude(id=id_actual).exists():
					data["valid"] = False
			elif type_val == "fecha_nacimiento":
				data["valid"] = validar_mayor_edad(obj_val)
		except Exception:
			pass
		return JsonResponse(data)	
	

	# 6. Procesamiento manual del POST (Seguro)
	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST.get("action")
		
		if action == "validate_data":
			return self.validate_data()

		try:
			if action == "edit":
				with transaction.atomic():
					empleado = self.get_object()
					usuario = empleado.usuario
					
					# Traemos la lista de campos bloqueados desde RefDet
					bloqueados=[]
					if self.is_self:
						bloqueados = self.get_bloqueados_db()

					# --- PROCESAMIENTO DINÁMICO DE CAMPOS ---
					# Si el campo está bloqueado, usamos el valor actual del objeto (empleado.campo)
					# Si NO está bloqueado, tomamos lo que viene por POST
					
					# 1. Campos lógicos y FKs complejas
					activo = empleado.activo if 'activo' in bloqueados else ("activo" in request.POST)
					sucursal_id = empleado.sucursal_id if 'sucursal' in bloqueados else isNULL(request.POST.get("sucursal"))
					
					# 2. Datos de Identidad
					ci = empleado.ci if 'ci' in bloqueados else isNULL(request.POST.get("ci"))
					ruc = empleado.ruc if 'ruc' in bloqueados else isNULL(request.POST.get("ruc"))
					nombre = empleado.nombre if 'nombre' in bloqueados else isNULL(request.POST.get("nombre"))
					apellido = empleado.apellido if 'apellido' in bloqueados else isNULL(request.POST.get("apellido"))
					
					# 3. Ubicación y Contacto
					nacionalidad_id = empleado.nacionalidad_id if 'nacionalidad' in bloqueados else isNULL(request.POST.get("nacionalidad"))
					ciudad_id = empleado.ciudad_id if 'ciudad' in bloqueados else isNULL(request.POST.get("ciudad"))
					barrio_id = empleado.barrio_id if 'barrio' in bloqueados else isNULL(request.POST.get("barrio"))
					direccion = empleado.direccion if 'direccion' in bloqueados else isNULL(request.POST.get("direccion"))
					celular = empleado.celular if 'celular' in bloqueados else isNULL(request.POST.get("celular"))
					telefono = empleado.telefono if 'telefono' in bloqueados else isNULL(request.POST.get("telefono"))
					email = empleado.email if 'email' in bloqueados else isNULL(request.POST.get("email"))
					
					# 4. Datos Personales
					fecha_nacimiento = empleado.fecha_nacimiento if 'fecha_nacimiento' in bloqueados else isNULL(request.POST.get("fecha_nacimiento"))
					sexo_id = empleado.sexo_id if 'sexo' in bloqueados else isNULL(request.POST.get("sexo"))
					estado_civil_id = empleado.estado_civil_id if 'estado_civil' in bloqueados else isNULL(request.POST.get("estado_civil"))
					tipo_sanguineo_id = empleado.tipo_sanguineo_id if 'tipo_sanguineo' in bloqueados else isNULL(request.POST.get("tipo_sanguineo"))
					fecha_vencimiento_ci = empleado.fecha_vencimiento_ci if 'fecha_vencimiento_ci' in bloqueados else isNULL(request.POST.get("fecha_vencimiento_ci"))
					
					# 5. Fechas Laborales
					fecha_ingreso = empleado.fecha_ingreso if 'fecha_ingreso' in bloqueados else isNULL(request.POST.get("fecha_ingreso"))
					fecha_egreso = empleado.fecha_egreso if 'fecha_egreso' in bloqueados else isNULL(request.POST.get("fecha_egreso"))

					# --- ASIGNACIÓN AL USUARIO (Sincronización) ---
					usuario.is_active = activo
					usuario.first_name = nombre
					usuario.last_name = apellido
					usuario.dni = ci
					usuario.username = ci
					usuario.email = email
					usuario.sucursal_id = sucursal_id
					
					# Imagen de perfil (Generalmente permitida, pero puedes bloquearla también)
					if 'image' not in bloqueados:
						if "image-clear" in request.POST:
							if usuario.image: usuario.image.delete(save=False)
							usuario.image = None
						if "image" in request.FILES:
							usuario.image = request.FILES["image"]
					usuario.save()

					# --- ASIGNACIÓN FINAL AL EMPLEADO ---
					empleado.activo = activo
					empleado.sucursal_id = sucursal_id
					empleado.ci = ci
					empleado.ruc = ruc
					empleado.nombre = nombre
					empleado.apellido = apellido
					empleado.nacionalidad_id = nacionalidad_id
					empleado.ciudad_id = ciudad_id
					empleado.barrio_id = barrio_id
					empleado.direccion = direccion
					empleado.celular = celular
					empleado.telefono = telefono
					empleado.email = email
					empleado.fecha_nacimiento = fecha_nacimiento
					empleado.sexo_id = sexo_id
					empleado.estado_civil_id = estado_civil_id
					empleado.tipo_sanguineo_id = tipo_sanguineo_id
					empleado.fecha_vencimiento_ci = fecha_vencimiento_ci
					empleado.fecha_ingreso = fecha_ingreso
					empleado.fecha_egreso = fecha_egreso

					# Manejo de Archivos PDF (Seguridad Dinámica)
					# Si 'archivo_pdf_ingreso' está en la lista de bloqueados, no procesamos el archivo del request
					if 'archivo_pdf_ingreso' not in bloqueados and "archivo_pdf_ingreso" in request.FILES:
						if empleado.archivo_pdf_ingreso: empleado.archivo_pdf_ingreso.delete(save=False)
						empleado.archivo_pdf_ingreso = request.FILES["archivo_pdf_ingreso"]
					
					if 'archivo_pdf_egreso' not in bloqueados and "archivo_pdf_egreso" in request.FILES:
						if empleado.archivo_pdf_egreso: empleado.archivo_pdf_egreso.delete(save=False)
						empleado.archivo_pdf_egreso = request.FILES["archivo_pdf_egreso"]

					if 'archivo_pdf_ci' not in bloqueados and "archivo_pdf_ci" in request.FILES:
						if empleado.archivo_pdf_ci: empleado.archivo_pdf_ci.delete(save=False)
						empleado.archivo_pdf_ci = request.FILES["archivo_pdf_ci"]

					empleado.save()
					data["id"] = empleado.id

			else:
				data["error"] = "No ha seleccionado ninguna opción"
		except Exception as e:
			data["error"] = str(e)
			
		return JsonResponse(data, safe=False)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["list_url"] = self.get_success_url()
		context["title"] = f"Perfil de {self.object.nombre} {self.object.apellido}"
		context["action"] = "edit"
		context["instance"] = self.object
		context["is_self"] = self.is_self
		return context

# class EmpleadoUpdate(PermissionMixin,UpdateView):
# 	# class EmpleadoUpdatePerfil(PermissionMixin, UpdateView):
# 	model = Empleado
# 	form_class = EmpleadoForm
# 	template_name = "empleado/create.html"
# 	success_url = reverse_lazy("dashboard")

# 	# Eliminamos la propiedad fija y la hacemos dinámica
# 	def get_permission_required(self):
# 		if self.request.resolver_match.url_name.endswith("_self"):
# 			return ("rh.change_empleado_self",) # Permiso para el empleado
# 		return ("rh.change_empleado",) # Permiso para el administrador
	
# 	@method_decorator(csrf_exempt)
# 	def dispatch(self, request, *args, **kwargs):
# 		self.is_self = self.request.resolver_match.url_name.endswith("_self")

# 		# Seguridad extra: Si es 'self' pero el usuario no tiene un empleado asociado
# 		if self.is_self and not hasattr(request.user, 'empleado'):
# 			raise Http404("Usted no tiene un perfil de empleado vinculado.")

# 		return super().dispatch(request, *args, **kwargs)
	
# 	def get_success_url(self):
# 		return reverse_lazy("dashboard") if self.is_self else reverse_lazy("empleado_list")
	
# 	# Obtener empleado asociado al usuario logueado
# 	def get_empleado(self):
# 		try:
# 			return Empleado.objects.get(usuario=self.request.user)
# 		except Empleado.DoesNotExist:
# 			raise Http404("No se encontró el perfil del empleado asociado al usuario.")
	
# 	def get_object(self, queryset=None):
# 		try:
# 			if self.is_self:
# 				return Empleado.objects.get(usuario=self.request.user)
# 			return Empleado.objects.get(pk=self.kwargs["pk"])
# 		except Empleado.DoesNotExist:
# 			raise Http404("No se encontró el perfil del empleado.")
	
# 	# Validar datos únicos
# 	def validate_data(self):
# 		data = {"valid": True}
# 		try:
# 			type = self.request.POST["type"]
# 			obj = self.request.POST["obj"].strip()
# 			id = self.get_object().id
# 			if type == "ci":
# 				if Empleado.objects.filter(ci__iexact=obj).exclude(id=id):
# 					data["valid"] = False
# 			if type == "ruc":
# 				if Empleado.objects.filter(ruc__iexact=obj).exclude(id=id):
# 					data["valid"] = False
# 			if type == "fecha_nacimiento":
# 				data["valid"] = validar_mayor_edad(obj)
			
# 		except:
# 			pass
# 		return JsonResponse(data)

# 	def post(self, request, *args, **kwargs):
# 		data = {}
# 		action = request.POST.get("action")
# 		try:
# 			if action == "edit":
# 					with transaction.atomic():
# 						empleado = self.get_object()
# 						usuario = empleado.usuario
# 						# Obtener datos del formulario
# 						activo = True if "on" in request.POST['activo'] else False
# 						ci = isNULL(request.POST["ci"])
# 						ruc = isNULL(request.POST["ruc"])
# 						nombre = isNULL(request.POST["nombre"])
# 						apellido = isNULL(request.POST["apellido"])
# 						sucursal_id = isNULL(request.POST["sucursal"])
# 						nacionalidad_id = isNULL(request.POST["nacionalidad"])
# 						ciudad_id = isNULL(request.POST["ciudad"])
# 						barrio_id = isNULL(request.POST["barrio"])
# 						direccion = isNULL(request.POST["direccion"])
# 						celular = isNULL(request.POST["celular"])
# 						telefono = isNULL(request.POST["telefono"])
# 						email = isNULL(request.POST["email"])
# 						fecha_nacimiento = isNULL(request.POST["fecha_nacimiento"])
# 						sexo_id = isNULL(request.POST["sexo"])
# 						estado_civil_id = isNULL(request.POST["estado_civil"])
# 						tipo_sanguineo_id = isNULL(request.POST["tipo_sanguineo"])
# 						fecha_vencimiento_ci = isNULL(request.POST["fecha_vencimiento_ci"])	
# 						archivo_pdf_ci = request.FILES.get("archivo_pdf_ci")
# 						fecha_ingreso = isNULL(request.POST["fecha_ingreso"])
# 						archivo_pdf_ingreso = request.FILES.get("archivo_pdf_ingreso")
# 						fecha_egreso = isNULL(request.POST["fecha_egreso"])
# 						archivo_pdf_egreso = request.FILES.get("archivo_pdf_egreso")

# 						# Actualizar datos del usuario
# 						usuario.is_active 	= activo
# 						usuario.first_name 	= nombre
# 						usuario.last_name 	= apellido
# 						usuario.dni 		= ci
# 						usuario.username 	= usuario.dni
# 						usuario.email 		= email
# 						usuario.sucursal_id = sucursal_id

# 						# Manejo de imagen
# 						if "image-clear" in request.POST:
# 							if usuario.image:
# 								usuario.image.delete(save=False)
# 							usuario.image = None
# 						if "image" in request.FILES:
# 							usuario.image = request.FILES["image"]

# 						usuario.save()

# 						# Asignar grupo si no está
# 						group = Group.objects.get(pk=settings.GROUPS.get("empleado"))
# 						# Mantener grupo existente y agregar el de empleado
# 						usuario.groups.add(group)

# 						# Actualizar datos del empleado
# 						empleado.activo 			= activo
# 						empleado.sucursal_id 		= sucursal_id
# 						empleado.ci 			 	= ci
# 						empleado.ruc 			 	= ruc
# 						empleado.nombre 		 	= nombre
# 						empleado.apellido 		 	= apellido
# 						empleado.nacionalidad_id 	= nacionalidad_id
# 						empleado.ciudad_id 		 	= ciudad_id
# 						empleado.barrio_id 		 	= barrio_id
# 						empleado.direccion 		 	= direccion
# 						empleado.celular 		 	= celular
# 						empleado.telefono 		 	= telefono
# 						empleado.email 			 	= email
# 						empleado.fecha_nacimiento  	= fecha_nacimiento
# 						empleado.sexo_id 		 	= sexo_id
# 						empleado.estado_civil_id	= estado_civil_id
# 						empleado.tipo_sanguineo_id	= tipo_sanguineo_id
# 						empleado.fecha_vencimiento_ci = fecha_vencimiento_ci
# 						empleado.fecha_ingreso 		= fecha_ingreso
# 						empleado.fecha_egreso 		= fecha_egreso
						
						
# 						if archivo_pdf_ci:
# 							# Si ya existía un archivo antes, lo borramos del disco
# 							if empleado.archivo_pdf_ci:
# 								empleado.archivo_pdf_ci.delete(save=False)
# 							# Asignamos el nuevo
# 							empleado.archivo_pdf_ci = archivo_pdf_ci
						
# 						if archivo_pdf_ingreso:
# 							if empleado.archivo_pdf_ingreso:
# 								empleado.archivo_pdf_ingreso.delete(save=False)
# 							empleado.archivo_pdf_ingreso = archivo_pdf_ingreso	
						
# 						if archivo_pdf_egreso:
# 							if empleado.archivo_pdf_egreso:
# 								empleado.archivo_pdf_egreso.delete(save=False)
# 							empleado.archivo_pdf_egreso = archivo_pdf_egreso
						
						
# 						empleado.save()
# 						data["id"] = empleado.id

# 			elif action == "validate_data":
# 				return self.validate_data()
# 			else:
# 				data["error"] = "No ha seleccionado ninguna opción"
# 		except Exception as e:
# 			data["error"] = str(e)
# 		return HttpResponse(json.dumps(data), content_type="application/json")


# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data()
# 		context["list_url"] = self.get_success_url()
# 		context["title"] = f" Perfil de {self.object.nombre} {self.object.apellido}"
# 		context["action"] = "edit"
# 		context["instance"] = self.object
# 		return context
	
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


class CVEmpleadoPDFView(View):
	template_name = 'empleado/cv_empleado_pdf.html'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.is_self = self.request.resolver_match.url_name.endswith("_self")
		return super().dispatch(request, *args, **kwargs)

	def get_object(self, queryset=None):
		try:
			if self.is_self:
				return Empleado.objects.select_related(
					'nacionalidad', 'ciudad', 'barrio', 'sexo', 'estado_civil'
				).get(usuario=self.request.user)
			return Empleado.objects.select_related(
				'nacionalidad', 'ciudad', 'barrio', 'sexo', 'estado_civil'
			).get(pk=self.kwargs["pk"])
		except Empleado.DoesNotExist:
			raise Http404("No se encontró el perfil del empleado.")

	def get(self, request, *args, **kwargs):
		empleado = self.get_object()
		context = {
			'empleado': empleado,
			'usuario': empleado.usuario,
			'fecha_generacion': getattr(request, 'timestamp', None),
		}
		html_string = render_to_string(self.template_name, context)
		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		pdf = html.write_pdf()

		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="cv_{empleado.nombre}_{empleado.apellido}.pdf"'
		return response
