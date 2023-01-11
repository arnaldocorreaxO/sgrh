from django.contrib import admin
from core.base.models import *

# Register your models here.
class ModeloAdminBase(admin.ModelAdmin):
    readonly_fields = ['usu_insercion',
                       'fec_insercion',
                       'usu_modificacion',
                       'fec_modificacion',
                       ]
    list_display = ['__str__',
                    'get_name_usu_insercion',
                    'fec_insercion',
                    'get_name_usu_modificacion',
                    'fec_modificacion',
                    ]


class ParametroAdmin(ModeloAdminBase):
    list_display = ('__str__','descripcion','activo',)
    search_fields = ('cod_parametro','descripcion',)

class MonedaAdmin(ModeloAdminBase):
    list_display = ('cod_moneda','denominacion','precio_compra','precio_venta')
    search_fields = ('denominacion',)


# REGISTRO DE MODELOS 
admin.site.register(Parametro,ParametroAdmin)
admin.site.register(Modulo,ModeloAdminBase)
admin.site.register(Empresa,ModeloAdminBase)
admin.site.register(Sucursal,ModeloAdminBase)
admin.site.register(Moneda,MonedaAdmin)
admin.site.register(TipoComprobante,ModeloAdminBase)
admin.site.register(SectorOperativo,ModeloAdminBase)