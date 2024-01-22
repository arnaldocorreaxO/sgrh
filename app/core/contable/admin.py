from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget, AutocompleteSelect

# Register your models here.
from core.base.admin import *
from core.contable.models import *


class PlanDeCuentaForm(forms.ModelForm):
    class Meta:
        # fields = ("cuenta_mayor",)
        widgets = {
            "cuenta_mayor": AutocompleteSelect(
                PlanDeCuenta.cuenta_mayor.field.remote_field,
                admin.site,
                attrs={"style": "width: 600px"},  # You can put any width you want.
            ),
            "denominacion": AdminTextInputWidget(
                attrs={"style": "width: 600px"},  # You can put any width you want.),
            ),
        }


class PlanDeCuentaAdmin(ModeloAdminBase):
    form = PlanDeCuentaForm
    # list_display = ('cod_moneda','denominacion','precio_compra','precio_venta')
    search_fields = ("denominacion",)
    autocomplete_fields = [
        "cuenta_mayor",
    ]


class EsquemaContableAdmin(ModeloAdminBase):
    list_display = [
        "nombre_campo",
        "tipo_dc",
        "rubro_contable",
        "tip_comprobante",
    ] + get_list_display()
    search_fields = ("denominacion",)
    list_filter = ("transaccion",)
    # raw_id_fields = ("rubro_contable", )
    autocomplete_fields = ["rubro_contable"]


class OperativaContableDetalleAdmin(ModeloAdminBase):
    list_display = [
        "__str__",
        # "rubro_contable",
        "metodo_interes",
        "uso_operacion",
    ]  # + get_list_display()
    search_fields = ("nombre_campo",)
    list_filter = ("operativa_contable",)
    # raw_id_fields = ("rubro_contable", )
    # autocomplete_fields = ["rubro_contable"]


# Register your models here.
# admin.site.register(TipoMovimiento, ModeloAdminBase)
admin.site.register(EsquemaContable, EsquemaContableAdmin)
admin.site.register(PlanDeCuenta, PlanDeCuentaAdmin)
admin.site.register(OperativaContable, ModeloAdminBase)
admin.site.register(OperativaContableDetalle, OperativaContableDetalleAdmin)
