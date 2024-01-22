import json
import os

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import CharField, F, Func, Q, Sum, Value
from django.db.models.fields import FloatField
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic.base import View
from weasyprint import CSS, HTML

from config import settings
from core.base.models import Empresa
from core.caja.procedures import sp_rptcaj012
from core.contable.models import Movimiento
from core.pos.models import Sale
from core.reports.forms import ReportForm
from core.security.mixins import PermissionMixin


# LISTA DE MOVIMIENTOS
class MovimientoListView(PermissionRequiredMixin, FormView):
    template_name = "movimiento/list.html"
    permission_required = "contable.view_movimiento"
    form_class = ReportForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "search":
                data = []
                start_date = request.POST["start_date"]
                end_date = request.POST["end_date"]
                if len(start_date) and len(end_date):
                    movi = (
                        Movimiento.objects.filter(
                            fec_movimiento__range=[start_date, end_date]
                        )
                        .values(
                            "fec_movimiento",
                            "cod_movimiento",
                            "cliente__cod_cliente",
                            "cliente__persona__nombre",
                            "cliente__persona__apellido",
                            "usu_insercion__cod_usuario",
                        )
                        .annotate(
                            importe=Sum("credito", output_field=FloatField()),
                        )
                    )
                else:
                    movi = (
                        Movimiento.objects.filter(
                            fec_movimiento__range=[start_date, end_date]
                        )
                        .values(
                            "fec_movimiento",
                            "cod_movimiento",
                            "cliente__cod_cliente",
                            "cliente__persona__nombre",
                            "usu_insercion__cod_usuario",
                        )
                        .annotate(
                            importe=Sum("credito", output_field=FloatField()),
                        )
                    )

                for i in movi:
                    data.append(i)
            else:
                data["error"] = "No ha ingresado una opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("trx_caja_create")
        context["title"] = "Listado de Movimientos en Caja"
        return context


class ReciboPrintView(View):
    success_url = reverse_lazy("movimiento_list")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # def get_height_ticket(self):
    #     sale = Sale.objects.get(pk=self.kwargs["pk"])
    #     height = 120
    #     increment = sale.saledetail_set.all().count() * 5.45
    #     height += increment
    #     return round(height)

    def get(self, request, *args, **kwargs):
        try:
            data = {}
            # fec_movimiento = self.kwargs["fec_movimiento"]
            # cod_movimiento = self.kwargs["cod_movimiento"]
            # cod_cliente = self.kwargs["cod_cliente"]
            # cod_usuario = self.kwargs["cod_usuario"]
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            print(self.kwargs)
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            recibo = sp_rptcaj012(request, *args, **self.kwargs)
            # recibo = Sale.objects.get(pk=1)
            print(recibo[0])
            context = {
                "recibo": recibo[0],
                "recibo_detalle": recibo,
                "empresa": Empresa.objects.first(),
            }

            template = get_template("movimiento/print/recibo.html")
            html_template = template.render(context).encode(encoding="UTF-8")
            url_css = os.path.join(
                settings.BASE_DIR, "static/lib/bootstrap-4.3.1/css/bootstrap.min.css"
            )
            pdf_file = HTML(
                string=html_template, base_url=request.build_absolute_uri()
            ).write_pdf(stylesheets=[CSS(url_css)], presentational_hints=True)
            response = HttpResponse(pdf_file, content_type="application/pdf")
            # response['Content-Disposition'] = 'filename="generate_html.pdf"'
            return response
        except Exception as e:
            print(e)
            data["error"] = str(e)
        return HttpResponseRedirect(self.success_url)
