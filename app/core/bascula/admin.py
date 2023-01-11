from django.contrib import admin
from core.base.admin import ModeloAdminBase
from core.bascula.models import *

# Register your models here.


class ConfigSerialModelAdmin(ModeloAdminBase):
    list_display = ('cod','sucursal', '__str__', 'descripcion',)

class MonedaAdmin(ModeloAdminBase):
    list_display = ('cod_moneda', 'denominacion',
                    'precio_compra', 'precio_venta')
    search_fields = ('denominacion',)

class MovimientoAdmin(ModeloAdminBase):
    list_display = ('id', 'fecha', 'nro_ticket','producto', 'fec_impresion')
    search_fields = ['id', 'cliente__denominacion', 'producto__denominacion', 'chofer__nombre',
                     'chofer__apellido', 'nro_ticket', 'vehiculo__matricula']
    readonly_fields = ('fecha', 'nro_ticket', 'fec_entrada', 'fec_salida',
                       'usu_insercion', 'fec_insercion', 'usu_modificacion', 'fec_modificacion',)
    # fields = ('nro_ticket','fecha','vehiculo','chofer','transporte','cliente','destino')
    # Consume muchos recursos (tarda mucho la consulta)
    list_editable = ['fec_impresion']
    list_filter = ['cliente', 'producto', 'vehiculo', 'chofer', 'fecha']
    list_per_page = 5

# REGISTRO DE MODELOS
admin.site.register(ConfigSerial, ConfigSerialModelAdmin)
admin.site.register(Transporte, ModeloAdminBase)
admin.site.register(MarcaVehiculo, ModeloAdminBase)
admin.site.register(Vehiculo, ModeloAdminBase)
admin.site.register(Chofer, ModeloAdminBase)
admin.site.register(Cliente, ModeloAdminBase)
admin.site.register(Categoria, ModeloAdminBase)
admin.site.register(Producto, ModeloAdminBase)
admin.site.register(Movimiento, MovimientoAdmin)
# admin.site.register(Movimiento, admin.ModelAdmin)
