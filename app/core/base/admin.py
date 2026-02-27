from django.contrib import admin

from core.base.models import *

# Register your models here.

_readonly_fields = [
    "usu_insercion",
    "fec_insercion",
    "usu_modificacion",
    "fec_modificacion",
]

_list_display = [
    "__str__",
    "get_name_usu_insercion",
    "fec_insercion",
    "get_name_usu_modificacion",
    "fec_modificacion",
]


def get_list_display():
    return _list_display


class ModeloAdminBase(admin.ModelAdmin):
    search_fields = []
    readonly_fields = _readonly_fields
    list_display = _list_display
    


class ParametroAdmin(ModeloAdminBase):
    list_display = (
        "__str__",
        "descripcion",
        "activo",
    )
    search_fields = (
        "cod_parametro",
        "descripcion",
    )


class MonedaAdmin(ModeloAdminBase):
    list_display = ("cod_moneda", "denominacion", "precio_compra", "precio_venta")
    search_fields = ("denominacion",)

class CiudadAdmin(ModeloAdminBase):
    # Usamos el nombre del método que crearemos abajo
    list_display = ["denominacion","get_distrito_denominacion", ]+_list_display
    search_fields = ("denominacion", "distrito__denominacion")
    list_filter = ("distrito",)

    # 1. Definimos el método para obtener el valor relacionado
    def get_distrito_denominacion(self, obj):
        return obj.distrito.denominacion
    
    # 2. Le damos un título a la columna en la interfaz
    get_distrito_denominacion.short_description = 'Distrito'
    
    # 3. (Opcional) Permitimos que se pueda ordenar por esta columna
    get_distrito_denominacion.admin_order_field = 'distrito__denominacion'
    
    # Optimización: evita una consulta por cada fila (N+1)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('distrito')

class BarrioAdmin(ModeloAdminBase):
    # Definimos el nombre del método en el list_display
    list_display = ( "denominacion","get_ciudad_denominacion",)
    search_fields = ("denominacion", "ciudad__denominacion")
    list_filter = ("ciudad",)

    # Método para obtener la denominación de la ciudad
    def get_ciudad_denominacion(self, obj):
        return obj.ciudad.denominacion
    
    # Configuración de la columna
    get_ciudad_denominacion.short_description = 'Ciudad' # Título de la columna
    get_ciudad_denominacion.admin_order_field = 'ciudad__denominacion' # Permite ordenar

    # Optimización: evita una consulta por cada fila (N+1)
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ciudad')   


class RefDetAdmin(ModeloAdminBase):
    list_display = [
        "id",
        "cod_referencia",
        # "denominacion",
    ] + _list_display
    search_fields = ("refcab__denominacion","denominacion",)
    list_filter = ("refcab",)


# REGISTRO DE MODELOS
admin.site.register(RefCab, ModeloAdminBase)
admin.site.register(RefDet, RefDetAdmin)
admin.site.register(Parametro, ParametroAdmin)
admin.site.register(Meses, ModeloAdminBase)
admin.site.register(Modulo, ModeloAdminBase)
admin.site.register(Transaccion, ModeloAdminBase)
admin.site.register(Empresa, ModeloAdminBase)
admin.site.register(Sucursal, ModeloAdminBase)
admin.site.register(Moneda, MonedaAdmin)
admin.site.register(Pais, ModeloAdminBase)
admin.site.register(Departamento, ModeloAdminBase)
admin.site.register(Ciudad, CiudadAdmin)
admin.site.register(Barrio, BarrioAdmin)
admin.site.register(Persona, ModeloAdminBase)
