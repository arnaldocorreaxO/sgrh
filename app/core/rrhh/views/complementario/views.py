from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, UpdateView
from core.base.views.generics import BaseListView
from core.rrhh.models import DocumentoComplementario, Empleado
from core.rrhh.forms.complementario.forms import DocumentoComplementarioForm
from core.rrhh.views.empleado.views import EmpleadoUsuarioMixin
from core.security.mixins import PermissionMixin
import json

# 📄 LISTADO
class DocumentoComplementarioList(BaseListView, EmpleadoUsuarioMixin, PermissionMixin):
    model = DocumentoComplementario
    template_name = "complementario/list.html"
    permission_required = "view_documentocomplementario"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            return DocumentoComplementario.objects.filter(empleado=empleado)
        except Empleado.DoesNotExist:
            return DocumentoComplementario.objects.none()

    def post(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("complementario_create")
        return self.enrich_context_with_empleado(context, prefijo="Documentos Complementarios")

# 🆕 CREACIÓN
class DocumentoComplementarioCreate(PermissionMixin, EmpleadoUsuarioMixin, CreateView):
    model = DocumentoComplementario
    form_class = DocumentoComplementarioForm
    template_name = "complementario/create.html"
    success_url = reverse_lazy("complementario_list")
    permission_required = "add_documentocomplementario"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get("action", "")
        try:
            if action == "add":
                form = self.get_form()
                if form.is_valid():
                    try:
                        empleado = Empleado.objects.get(usuario=request.user)
                        instance = form.save(commit=False)
                        instance.empleado = empleado
                        instance.save()
                        data["success"] = True
                    except Empleado.DoesNotExist:
                        data["error"] = "No se encontró un empleado vinculado al usuario actual"
                else:
                    data["error"] = form.errors
            elif action == "validate_data":
                return JsonResponse({"valid": True})
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_url"] = self.success_url
        context["action"] = "add"
        return self.enrich_context_with_empleado(context, prefijo="Agregar Documento Complementario")

# ✏️ EDICIÓN
class DocumentoComplementarioUpdate(PermissionMixin, EmpleadoUsuarioMixin, UpdateView):
    model = DocumentoComplementario
    form_class = DocumentoComplementarioForm
    template_name = "complementario/create.html"
    success_url = reverse_lazy("complementario_list")
    permission_required = "change_documentocomplementario"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            return DocumentoComplementario.objects.get(pk=self.kwargs["pk"], empleado=empleado)
        except (Empleado.DoesNotExist, DocumentoComplementario.DoesNotExist):
            raise Http404("No se encontró el documento complementario asociado al usuario.")

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get("action", "")
        try:
            if action == "edit":
                form = self.get_form()
                if form.is_valid():
                    form.instance.empleado = self.object.empleado  # reforzar asociación
                    form.save()
                    data["success"] = True
                else:
                    data["error"] = form.errors
            elif action == "validate_data":
                return JsonResponse({"valid": True})
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_url"] = self.success_url
        context["action"] = "edit"
        context["instance"] = self.object
        return self.enrich_context_with_empleado(context, prefijo="Modificar Documento Complementario")

# 🗑️ ELIMINACIÓN
class DocumentoComplementarioDelete(PermissionMixin, DeleteView):
    model = DocumentoComplementario
    template_name = "complementario/delete.html"
    success_url = reverse_lazy("complementario_list")
    permission_required = "delete_documentocomplementario"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
            data["success"] = True
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Notificación de eliminación"
        context["list_url"] = self.success_url
        return context
