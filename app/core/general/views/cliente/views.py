import json
import math

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.security.mixins import PermissionMixin
from core.socio.forms import Cliente, ClienteForm


class ClienteList(PermissionMixin, ListView):
    model = Cliente
    template_name = "cliente/list.html"
    permission_required = "view_cliente"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        # print(request.POST)
        action = request.POST["action"]

        try:
            if action == "search":
                data = []

                _start = request.POST["start"]
                _length = request.POST["length"]
                _search = request.POST["search[value]"]

                _order = []

                for i in range(9):
                    _column_order = f"order[{i}][column]"
                    # print('Column Order:',_column_order)
                    if _column_order in request.POST:
                        _column_number = request.POST[_column_order]
                        _order.append(
                            request.POST[f"columns[{_column_number}][data]"].split(".")[
                                0
                            ]
                        )
                    if f"order[{i}][dir]" in request.POST:
                        _dir = request.POST[f"order[{i}][dir]"]
                        if _dir == "desc":
                            _order[i] = f"-{_order[i]}"

                _where = "1 = 1"
                qs = Cliente.objects.filter().extra(where=[_where]).order_by(*_order)
                if len(_search):
                    if _search.isnumeric():
                        qs = (
                            (
                                qs.filter(
                                    Q(cod_cliente__exact=_search)
                                    | Q(persona__ci__exact=_search)
                                )
                            )
                            .exclude(activo=False)
                            .order_by("cod_cliente")
                        )
                    else:
                        qs = (
                            qs.filter(
                                Q(persona__nombre__icontains=_search)
                                | Q(persona__apellido__icontains=_search)
                            )
                            .exclude(activo=False)
                            .order_by("cod_cliente")
                        )

                total = qs.count()
                print(total)

                if _start and _length:
                    start = int(_start)
                    length = int(_length)
                    page = math.ceil(start / length) + 1
                    per_page = length

                if _length == "-1":
                    qs = qs[start:]
                else:
                    qs = qs[start : start + length]

                position = start + 1
                for i in qs:
                    item = i.toJSON()
                    # item['position'] = position
                    data.append(item)
                    position += 1
                # print(data)
                data = {
                    "data": data,
                    "page": page,  # [opcional]
                    "per_page": per_page,  # [opcional]
                    "recordsTotal": total,
                    "recordsFiltered": total,
                }
            else:
                data["error"] = "No ha ingresado una opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("cliente_create")
        context["title"] = "Listado de Clientes"
        return context


class ClienteCreate(PermissionMixin, CreateView):
    model = Cliente
    template_name = "socio/create.html"
    form_class = ClienteForm
    success_url = reverse_lazy("cliente_list")
    permission_required = "add_cliente"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            if type == "denominacion":
                if Cliente.objects.filter(denominacion__iexact=obj):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "add":
                data = self.get_form().save()
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_cliente":
                data = []
                term = request.POST["term"]
                qs = Cliente.objects.filter(
                    Q(activo__exact=True)
                    & (
                        Q(cod_cliente__icontains=term)
                        | Q(nro_socio__icontains=term)
                        | Q(persona__ci__icontains=term)
                        | Q(persona__nombre__icontains=term)
                        | Q(persona__apellido__icontains=term)
                    )
                ).order_by("persona__apellido", "persona__nombre")[0:10]

                data = [{"id": "", "text": "------------"}]

                for c in qs:
                    # Como codigo de cliente no tiene ID, retornamos asi, o sino no funciona SELECT2
                    # una matriz de objetos que contienen, como mínimo, las propiedades 'id' y 'text'
                    item = {}
                    item["id"] = c.cod_cliente
                    item["text"] = "{} / {}".format(str(c), c.nro_socio)
                    data.append(item)
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Nuevo registro de Cliente"
        context["action"] = "add"
        return context


class ClienteUpdate(PermissionMixin, UpdateView):
    model = Cliente
    template_name = "cliente/create.html"
    form_class = ClienteForm
    success_url = reverse_lazy("cliente_list")
    permission_required = "change_cliente"

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
            if type == "denominacion":
                if Cliente.objects.filter(denominacion__iexact=obj).exclude(id=id):
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
        context["title"] = "Edición de Cliente"
        context["action"] = "edit"
        return context


class ClienteDelete(PermissionMixin, DeleteView):
    model = Cliente
    template_name = "cliente/delete.html"
    success_url = reverse_lazy("cliente_list")
    permission_required = "delete_cliente"

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
