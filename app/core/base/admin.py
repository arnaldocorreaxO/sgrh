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


class RefDetAdmin(ModeloAdminBase):
    list_display = [
        "cod_referencia",
    ] + _list_display
    search_fields = ("refcab__denominacion",)
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
admin.site.register(Ciudad, ModeloAdminBase)
admin.site.register(Barrio, ModeloAdminBase)
admin.site.register(Persona, ModeloAdminBase)
