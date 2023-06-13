import json
import math

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.base.models import Persona
from core.base.utils import YYYY_MM_DD
from core.prestamo.forms import SolicitudPrestamoForm
from core.prestamo.models import SolicitudPrestamo
from core.prestamo.procedures import sp_alta_solicitud_prestamo
from core.security.mixins import PermissionMixin
from core.socio.forms import SocioForm


class SolicitudPrestamoList(PermissionRequiredMixin, ListView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/list.html"
    permission_required = "view_solicitudprestamo"

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

                # _order = ["aprobado"]
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

                _where = "'' = %s"
                persona = None
                if len(_search):
                    pass
                    # if _search.isnumeric():
                    # 	_search = "%" + _search.replace(' ', '%') + "%"
                    # 	_where = " upper(nro_solicitud ) LIKE upper(%s)"
                    # else:
                    # 	persona = Persona.objects.filter(nombre__icontains=_search).first()
                    # 	print(persona)

                # print(_where)
                # qs = SolicitudPrestamo.objects\
                # 				.filter(persona__nombre__icontains=_search)\
                # 				.extra(where=[_where], params=[_search])\
                # 				.order_by(*_order)
                qs = SolicitudPrestamo.objects.filter(
                    Q(nro_solicitud__icontains=_search)
                    | Q(socio__persona__nombre__icontains=_search)
                    | Q(socio__persona__apellido__icontains=_search)
                ).order_by(*_order)

                # print(qs.query)
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
        context["create_url"] = reverse_lazy("solicitud_prestamo_create")
        context["title"] = "Listado de Solicitudes de Prestamos "
        return context


class SolicitudPrestamoCreate(PermissionMixin, CreateView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/create.html"
    form_class = SolicitudPrestamoForm
    success_url = reverse_lazy("solicitud_prestamo_list")
    permission_required = "add_solicitudprestamo"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            if type == "denominacion":
                if SolicitudPrestamo.objects.filter(denominacion__iexact=obj):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "add":
                # RETORNA EL NRO. DE SOLICITUD GENERADA
                data = sp_alta_solicitud_prestamo(request)
                if data["rtn"] == 0:
                    # with transaction.atomic():
                    #     solicitud = SolicitudPrestamo()
                    #     solicitud.activo = True if request.POST["activo"] else False
                    #     solicitud.nro_solicitud = data["val"]  # NRO_SOLICITUD
                    #     solicitud.fec_solicitud = YYYY_MM_DD(
                    #         request.POST["fec_solicitud"]
                    #     )
                    #     solicitud.fec_charla = YYYY_MM_DD(request.POST["fec_charla"])
                    #     solicitud.sucursal_id = request.POST["sucursal"]
                    #     solicitud.persona_id = request.POST["persona"]
                    #     solicitud.telefono = request.POST["telefono"]
                    #     solicitud.promocion_id = request.POST["promocion"]
                    #     solicitud.socio_proponente_id = request.POST["socio_proponente"]
                    #     solicitud.save()
                    data["msg"] += "<br> NRO. DE SOLICITUD " + data["val"]
                # CONCATENAMOS DICCIONARIO
                # data.update(data_proc)
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
        context["title"] = "Nuevo registro Solicitud de Prestamo"
        context["action"] = "add"
        return context


class SolicitudPrestamoUpdate(PermissionMixin, UpdateView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/create.html"
    form_class = SolicitudPrestamoForm
    success_url = reverse_lazy("solicitud_prestamo_list")
    permission_required = "change_solicitudprestamo"

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
                if SolicitudPrestamo.objects.filter(denominacion__iexact=obj).exclude(
                    id=id
                ):
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
        context["title"] = "Edición de una Solicitud de Ingreso"
        context["action"] = "edit"
        return context


# class AprobarSolicitudPrestamoUpdate(PermissionMixin, UpdateView):
#     model = SolicitudPrestamo
#     template_name = "solicitud_prestamo/form_aprobar_solicitud.html"
#     form_class = AprobarSolicitudPrestamoForm
#     success_url = reverse_lazy("solicitud_prestamo_list")
#     permission_required = "change_solicitudprestamo"

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().dispatch(request, *args, **kwargs)

#     def validate_data(self):
#         data = {"valid": True}
#         try:
#             type = self.request.POST["type"]
#             obj = self.request.POST["obj"].strip()
#             id = self.get_object().id
#             if type == "denominacion":
#                 if SolicitudPrestamo.objects.filter(denominacion__iexact=obj).exclude(
#                     id=id
#                 ):
#                     data["valid"] = False
#         except:
#             pass
#         return JsonResponse(data)

#     def post(self, request, *args, **kwargs):
#         data = {}
#         action = request.POST["action"]
#         print(request.POST["aprobado"])
#         try:
#             if action == "edit":
#                 if request.POST["aprobado"] not in ("unknown"):
#                     data = sp_aprobar_solicitud_ingreso(request)
#                 else:
#                     data["error"] = "No ha seleccionado Aprobado (Si/No)"

#             elif action == "validate_data":
#                 return self.validate_data()
#             else:
#                 data["error"] = "No ha seleccionado ninguna opción"
#         except Exception as e:
#             data["error"] = str(e)
#         return HttpResponse(json.dumps(data), content_type="application/json")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data()
#         context["list_url"] = self.success_url
#         context["title"] = "Aprobar Solicitud de Ingreso de Socio"
#         context["action"] = "edit"
#         return context


class SolicitudPrestamoDelete(PermissionMixin, DeleteView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/delete.html"
    success_url = reverse_lazy("solicitud_prestamo_list")
    permission_required = "delete_solicitudprestamo"

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
