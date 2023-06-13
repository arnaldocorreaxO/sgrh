import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.db.models.fields import FloatField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, FormView

from core.base.utils import YYYY_MM_DD
from core.caja.forms import *
from core.caja.procedures import *
from core.contable.models import Movimiento, TmpMovimiento
from core.reports.forms import ReportForm
from core.security.mixins import PermissionMixin
from core.socio.models import PromocionIngreso, Socio, SolicitudIngreso


# TRANSACCIONES EN CAJA
class TransaccionCreateView(PermissionMixin, FormView):
    # model = Movimiento
    template_name = "transaccion/create.html"
    form_class = TransaccionCajaForm
    # success_url = reverse_lazy("purchase_list")
    permission_required = "add_movimiento"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # # TODO: Podemos utilizar para validar montos
    # # def validate_provider(self):
    # #     data = {"valid": True}
    # #     try:
    # #         type = self.request.POST["type"]
    # #         obj = self.request.POST["obj"].strip()
    # #         if type == "name":
    # #             if Provider.objects.filter(name__iexact=obj):
    # #                 data["valid"] = False
    # #         elif type == "ruc":
    # #             if Provider.objects.filter(ruc__iexact=obj):
    # #                 data["valid"] = False
    # #         elif type == "mobile":
    # #             if Provider.objects.filter(mobile=obj):
    # #                 data["valid"] = False
    # #         elif type == "email":
    # #             if Provider.objects.filter(email=obj):
    # #                 data["valid"] = False
    # #     except:
    # #         pass
    # #     return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        action = request.POST["action"]
        data = {}
        try:
            if action == "list_trx":
                data = []
                fec_movimiento = YYYY_MM_DD(request.POST["fec_movimiento"])
                cod_movimiento = request.POST["cod_movimiento"]
                rows = (
                    TmpMovimiento.objects.values(
                        "transaccion__cod_transaccion",
                        "moneda__iso",
                        "transaccion__abreviatura",
                    )
                    .filter(
                        fec_movimiento__iexact=fec_movimiento,
                        cod_movimiento__iexact=cod_movimiento,
                    )
                    .annotate(importe=Sum("credito", output_field=FloatField()))
                    .order_by("transaccion__cod_transaccion")
                )
                for row in rows:
                    data.append(
                        {
                            "cod_transaccion": row["transaccion__cod_transaccion"],
                            "abr_transaccion": row["transaccion__abreviatura"],
                            "iso_moneda": row["moneda__iso"],
                            "importe": row["importe"],
                        }
                    )
            elif action == "add":
                data = sp_PTRX_GRABAR_CAJA(request)

        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = TransaccionCajaForm(request=self.request)
        context["list_url"] = self.success_url
        context["title"] = "Transacciones en Caja"
        context["action"] = "add"
        return context


# INGRESO DE NUEVO SOCIO
class Trx700FormView(PermissionMixin, FormView):
    template_name = "transaccion/trx700_modal.html"
    permission_required = "add_movimiento"
    form_class = Trx700Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "search":
                if request.user.has_perm("contable.add_movimiento"):
                    fec_movimiento = request.POST["fec_movimiento"]
                    cod_movimiento = request.POST["cod_movimiento"]
                    nro_documento = request.POST["nro_recibo"].split("/")
                    socio_id = request.POST["socio_id"]

                    if socio_id:
                        promocion_solicitud_ingreso = SolicitudIngreso.objects.filter(
                            socio__id__iexact=socio_id
                        ).first()
                        promocion = PromocionIngreso.objects.filter(
                            id__iexact=promocion_solicitud_ingreso.promocion_id
                        ).first()

                        form = self.form_class
                        context = self.get_context_data()
                        context["form"] = form
                        context["action"] = "add"
                        context["action_url"] = reverse_lazy("trx700_create")
                        data["data"] = promocion.toJSON()
                        data["html_form"] = render_to_string(
                            self.template_name, context, request=request
                        )
                    else:
                        data[
                            "error"
                        ] = "Debe selecccionar un socio para esta transaccion"
                else:
                    data["error"] = "No tiene permisos para editar"
            elif action == "add":
                data = sp_trx700(request)
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("trx_caja_create")
        context["title"] = "INGRESO DE NUEVO SOCIO"
        return context


# APORTES SOCIALES
class Trx701FormView(PermissionMixin, FormView):
    template_name = "transaccion/trx701_modal.html"
    permission_required = "add_movimiento"
    form_class = Trx701Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "search":
                if request.user.has_perm("contable.add_movimiento"):
                    socio_id = request.POST["socio_id"]

                    if socio_id:
                        cuota = sp_fnCUOTA_OBLICACION_CUENTA(request, "APR")
                        form = self.form_class
                        context = self.get_context_data()
                        context["form"] = form
                        context["action"] = "add"
                        context["action_url"] = reverse_lazy("trx701_create")
                        data["data"] = cuota
                        data["html_form"] = render_to_string(
                            self.template_name, context, request=request
                        )
                    else:
                        data[
                            "error"
                        ] = "Debe selecccionar un socio para esta transaccion"
                else:
                    data["error"] = "No tiene permisos para editar"
            elif action == "add":
                data = sp_trx701(request)
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("trx_caja_create")
        context["title"] = "APORTES DE CAPITAL"
        return context


# APORTES DE SOLIDARIDAD
class Trx702FormView(PermissionMixin, FormView):
    template_name = "transaccion/trx702_modal.html"
    permission_required = "add_movimiento"
    form_class = Trx702Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "search":
                if request.user.has_perm("contable.add_movimiento"):
                    socio_id = request.POST["socio_id"]

                    if socio_id:
                        cuota = sp_fnCUOTA_OBLICACION_CUENTA(request, "SLD")
                        form = self.form_class
                        context = self.get_context_data()
                        context["form"] = form
                        context["action"] = "add"
                        context["action_url"] = reverse_lazy("trx702_create")
                        data["data"] = cuota
                        data["html_form"] = render_to_string(
                            self.template_name, context, request=request
                        )
                    else:
                        data[
                            "error"
                        ] = "Debe selecccionar un socio para esta transaccion"
                else:
                    data["error"] = "No tiene permisos para editar"
            elif action == "add":
                data = sp_trx702(request)
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("trx_caja_create")
        context["title"] = "APORTES DE SOLIDARIDAD"
        return context
