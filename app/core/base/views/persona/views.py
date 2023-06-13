import json
import json as simplejson
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from config.identificaciones import get_consultar_datos_persona
from config.sqlserver_copy import get_ruc, get_ruc_
from core.base.forms import Persona, PersonaForm
from core.security.mixins import PermissionMixin


# Obtener datos de la persona de la Base de Datos de Identificaciones
def get_datos_persona(request):
    # import pdb; pdb.set_trace()
    vCi = str(request.GET.get("ci", "X"))
    # print("*" * 10)
    # print(vCi)
    persona = get_consultar_datos_persona(vCedula=vCi)
    # print(persona)
    return HttpResponse(simplejson.dumps(persona), content_type="application/json")


class PersonaList(PermissionMixin, ListView):
    model = Persona
    template_name = "persona/list.html"
    permission_required = "view_persona"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("persona_create")
        context["title"] = "Listado de Personas"
        return context


class PersonaCreate(PermissionMixin, CreateView):
    model = Persona
    template_name = "persona/create.html"
    form_class = PersonaForm
    success_url = reverse_lazy("persona_list")
    permission_required = "add_persona"

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
                if Persona.objects.filter(ci__iexact=obj):
                    data["valid"] = False
            if type == "ruc":
                if Persona.objects.filter(ruc__iexact=obj):
                    data["valid"] = False
            if type == "fec_nacimiento":
                import datetime as dt

                fec_nacimiento = datetime.strptime(
                    obj, "%d/%m/%Y"
                )  # Este del from datetime
                edad = relativedelta(dt.datetime.now(), fec_nacimiento)
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
                data = self.get_form().save()
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
        context["title"] = "Nuevo registro de una Persona"
        context["action"] = "add"
        return context


class PersonaUpdate(PermissionMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    # template_name = "persona/create.html"
    template_name = "transaccion/trx700.html"

    success_url = reverse_lazy("persona_list")
    permission_required = "change_persona"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            id = self.get_object().id
            if type == "ci":
                if Persona.objects.filter(ci__iexact=obj).exclude(id=id):
                    data["valid"] = False
            if type == "ruc":
                if Persona.objects.filter(ruc__iexact=obj).exclude(id=id):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "edit":
                data = self.get_form().save()
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
        context["title"] = "Edición de una Persona"
        context["action"] = "edit"
        return context


class PersonaDelete(PermissionMixin, DeleteView):
    model = Persona
    template_name = "persona/delete.html"
    success_url = reverse_lazy("persona_list")
    permission_required = "delete_persona"

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
