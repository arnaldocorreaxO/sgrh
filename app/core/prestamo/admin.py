from django.contrib import admin

from core.base.admin import ModeloAdminBase, get_list_display
from core.prestamo.models import *


# Register your models here.
class EsquemaContableAdmin(ModeloAdminBase):
    # list_display = ('id',)
    # search_fields = ('denominacion',)
    list_filter = (
        "plazo",
        "vencimiento",
        "estado_cliente",
        "situacion_prestamo",
        "vinculado",
    )
    # raw_id_fields = ("rubro_contable", )
    autocomplete_fields = ["rubro_capital"]


# Register your models here.
# admin.site.register(Plazo, ModeloAdminBase)
# admin.site.register(SituacionPrestamo, ModeloAdminBase)
# admin.site.register(EsquemaContable, EsquemaContableAdmin)
# admin.site.register(TipoPrestamo, ModeloAdminBase)
# admin.site.register(ClasificacionPorDestino, ModeloAdminBase)
# admin.site.register(DestinoPrestamo, ModeloAdminBase)
# admin.site.register(EstadoDesembolso, ModeloAdminBase)
# admin.site.register(SituacionSolicitud, ModeloAdminBase)
# admin.site.register(NivelAprobacion, ModeloAdminBase)
