from django.contrib import admin

from core.base.admin import ModeloAdminBase, get_list_display
from core.socio.models import (
    CalificacionSocio,
    EstadoSocio,
    ObligacionCuenta,
    PromocionIngreso,
    Socio,
    SolicitudIngreso,
    TipoCuenta,
)


class ObligacionCuentaAdmin(ModeloAdminBase):
    list_display = [
        "tip_cuenta",
        "anho",
        "mes_desde",
        "mes_hasta",
        "mto_cuota_mensual",
    ] + get_list_display()
    search_fields = ("tip_cuenta",)
    list_filter = ("anho",)


# Register your models here.
admin.site.register(CalificacionSocio, ModeloAdminBase)
admin.site.register(EstadoSocio, ModeloAdminBase)
admin.site.register(Socio, ModeloAdminBase)
admin.site.register(SolicitudIngreso, ModeloAdminBase)
admin.site.register(PromocionIngreso, ModeloAdminBase)
admin.site.register(TipoCuenta, ModeloAdminBase)
admin.site.register(ObligacionCuenta, ObligacionCuentaAdmin)
