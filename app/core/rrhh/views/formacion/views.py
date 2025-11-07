import json

from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, UpdateView


from core.base.views.generics import BaseListView
from core.rrhh.forms.formacion.forms import FormacionForm

from core.rrhh.models import Empleado, FormacionAcademica
from core.rrhh.views.empleado.views import EmpleadoUsuarioMixin
from core.security.mixins import PermissionMixin


class FormacionList(BaseListView,EmpleadoUsuarioMixin, PermissionMixin):
	model = FormacionAcademica
	template_name = "formacion/list.html"
	permission_required = "view_formacionacademica"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		try:
			empleado = Empleado.objects.get(usuario=self.request.user)
			return FormacionAcademica.objects.filter(empleado=empleado)
		except Empleado.DoesNotExist:
			return FormacionAcademica.objects.none()

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST["action"]
		try:
			if action == "search":
				data = self.handle_search(request)
				print(data.content.decode())  # Muestra el JSON como string legible

			else:
				data["error"] = "No ha ingresado una opción"
		except Exception as e:
			data["error"] = str(e)
		return HttpResponse(data, content_type="application/json"
		)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["create_url"] = reverse_lazy("formacion_create")
		#Titulo con el nombre del empleado
		return self.enrich_context_with_empleado(context, prefijo="Formación Académica")


class FormacionCreate(PermissionMixin,EmpleadoUsuarioMixin,CreateView):
	model = FormacionAcademica
	form_class = FormacionForm
	template_name = "formacion/create.html"
	success_url = reverse_lazy("formacion_list")
	permission_required = "add_formacionacademica"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	 # Obtener la formacion academica del empleado asociado al usuario logueado
	def get_formacion_academica_empleado(self):
		try:
			empleado = Empleado.objects.get(usuario=self.request.user)
			return FormacionAcademica.objects.filter(empleado=empleado)
		except Empleado.DoesNotExist:
			raise Http404("No se encontró el perfil del empleado asociado al usuario.")
	
	# Sobrescribir get_object para obtener la formacion academica del empleado usuario logueado
	def get_object(self, queryset=None):
		formacion = self.get_formacion_academica_empleado()
		if formacion:
			return formacion
		return FormacionAcademica()
	
	def validate_data(self):
		data = {"valid": True}
		try:
			pass
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST["action"]
		try:
			if action == "add":
				form = self.get_form()
				if form.is_valid():                                       
					# 🔗 Asociar el empleado actual al usuario de sesión
					try:
						empleado = Empleado.objects.get(usuario=request.user)
						instance = form.save_with_empleado(empleado=empleado)
					except Empleado.DoesNotExist:
						data["error"] = "No se encontró un empleado vinculado al usuario actual"
						return JsonResponse(data, status=400)
				
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
		context["list_url"] = self.success_url
		context["action"] = "add"
		#Titulo con el nombre del empleado
		return self.enrich_context_with_empleado(context, prefijo="Agregar Formación Académica")



class FormacionUpdate(PermissionMixin,EmpleadoUsuarioMixin,UpdateView):
	model = FormacionAcademica
	form_class = FormacionForm
	template_name = "formacion/create.html"
	success_url = reverse_lazy("formacion_list")
	permission_required = "change_formacionacademica"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().dispatch(request, *args, **kwargs)
	
	def get_object(self, queryset=None):
		try:
			empleado = Empleado.objects.get(usuario=self.request.user)
			return FormacionAcademica.objects.get(pk=self.kwargs["pk"], empleado=empleado)
		except (Empleado.DoesNotExist, FormacionAcademica.DoesNotExist):
			raise Http404("No se encontró la formación académica asociada al usuario.")


	def validate_data(self):
		data = {"valid": True}
		try:
			pass
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST["action"]
		try:
			if action == "edit":
				form = self.get_form()
				if form.is_valid():                                       
					# 🔗 Asociar el empleado actual al usuario de sesión
					try:
						#El empleado ya está asociado al objeto
						#Acá es solo reforzar la asociación.
						empleado = Empleado.objects.get(usuario=request.user)
						form.instance.empleado = empleado
						form.save()

					except Empleado.DoesNotExist:
						data["error"] = "No se encontró un empleado vinculado al usuario actual"
						return JsonResponse(data, status=400)
				
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
		context["list_url"] = self.success_url
		context["action"] = "edit"
		context["instance"] = self.object
		#Titulo con el nombre del empleado
		return self.enrich_context_with_empleado(context, prefijo="Modificar Formación Académica")



class FormacionDelete(PermissionMixin, DeleteView):
	model = FormacionAcademica
	template_name = "formacion/delete.html"
	success_url = reverse_lazy("formacion_list")
	permission_required = "delete_formacionacademica"

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


