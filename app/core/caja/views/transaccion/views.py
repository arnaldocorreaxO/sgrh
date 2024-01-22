import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import CharField, F, Func, Q, Sum, Value
from django.db.models.fields import FloatField
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from core.base.utils import YYYY_MM_DD
from core.caja.forms import *
from core.caja.procedures import *
from core.contable.models import TmpMovimiento
from core.security.mixins import PermissionMixin
from core.socio.models import PromocionIngreso, SolicitudIngreso


# TRANSACCIONES EN CAJA
class TransaccionCajaFormView(PermissionRequiredMixin, FormView):
    # model = Movimiento
    template_name = "caja/transaccion/create.html"
    form_class = TransaccionCajaForm
    success_url = reverse_lazy("movimiento_list")
    permission_required = "contable.add_movimiento"

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
                        "cod_movimiento",
                        "cuenta_operativa",
                        "nro_documento",
                    )
                    .filter(
                        fec_movimiento__iexact=fec_movimiento,
                        cod_movimiento__iexact=cod_movimiento,
                    )
                    .exclude(transaccion_id=206)
                    .annotate(importe=Sum("credito", output_field=FloatField()))
                    .order_by("transaccion__cod_transaccion")
                )
                for row in rows:
                    data.append(
                        {
                            "cod_movimiento": row["cod_movimiento"],
                            "cuenta_operativa": row["cuenta_operativa"],
                            "nro_documento": row["nro_documento"],
                            "cod_transaccion": row["transaccion__cod_transaccion"],
                            "abr_transaccion": row["transaccion__abreviatura"],
                            "iso_moneda": row["moneda__iso"],
                            "importe": row["importe"],
                        }
                    )
            elif action == "del_trx":
                print(request.POST)
                cod_movimiento = request.POST["cod_movimiento"]
                cod_transaccion = request.POST["cod_transaccion"]
                cuenta_operativa = request.POST["cuenta_operativa"]
                nro_documento = request.POST["nro_documento"]
                TmpMovimiento.objects.filter(
                    cod_movimiento=cod_movimiento,
                    transaccion__cod_transaccion=cod_transaccion,
                    cuenta_operativa=cuenta_operativa,
                    nro_documento=nro_documento,
                ).delete()
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
        context["modulo"] = "CJ"  # POR AHORA SOLO ENVIAMOS CJ = CAJA
        context["tipo_acceso"] = "C"  # C=CAJA D=DIARIO
        return context


# INGRESO DE NUEVO SOCIO
class Trx700FormView(PermissionRequiredMixin, FormView):
    template_name = "caja/transaccion/trx700_modal.html"
    permission_required = "contable.add_movimiento"
    form_class = Trx700Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        print(request.POST)
        try:
            if action == "open_modal_trx":
                if request.user.has_perm("contable.add_movimiento"):
                    fec_movimiento = request.POST["fec_movimiento"]
                    cod_movimiento = request.POST["cod_movimiento"]
                    nro_documento = request.POST["nro_recibo"].split("/")
                    cod_cliente = request.POST["cod_cliente"]
                    print(cod_cliente)
                    if cod_cliente:
                        promocion_solicitud_ingreso = SolicitudIngreso.objects.filter(
                            cliente__cod_cliente__iexact=cod_cliente
                        ).first()
                        if promocion_solicitud_ingreso:
                            print(promocion_solicitud_ingreso)
                            promocion = PromocionIngreso.objects.filter(
                                id__iexact=promocion_solicitud_ingreso.promocion_id
                            ).first()
                            print(promocion)

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
                                "info"
                            ] = "No se encontró promocion de ingreso para el socio"

                    else:
                        data[
                            "info"
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
class Trx701FormView(PermissionRequiredMixin, FormView):
    template_name = "caja/transaccion/trx701_modal.html"
    permission_required = "contable.add_movimiento"
    form_class = Trx701Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "open_modal_trx":
                if request.user.has_perm("contable.add_movimiento"):
                    cod_cliente = request.POST["cod_cliente"]

                    if cod_cliente:
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
class Trx702FormView(PermissionRequiredMixin, FormView):
    template_name = "caja/transaccion/trx702_modal.html"
    permission_required = "contable.add_movimiento"
    form_class = Trx702Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "open_modal_trx":
                if request.user.has_perm("contable.add_movimiento"):
                    cod_cliente = request.POST["cod_cliente"]

                    if cod_cliente:
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
