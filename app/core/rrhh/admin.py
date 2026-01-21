from django.contrib import admin
from django import forms


# Register your models here.
from core.base.admin import ModeloAdminBase
from core.rrhh.models import *
from core.base.admin import _list_display,_readonly_fields
from django.contrib.admin import SimpleListFilter

class InstitucionAdminForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_institucion'].queryset = RefDet.objects.filter(refcab__cod_referencia__exact='TIPO_INSTITUCION')
        self.fields['tipo_funcion'].queryset = RefDet.objects.filter(refcab__cod_referencia__exact='TIPO_FUNCION_INSTITUCION')

class InstitucionAdmin(ModeloAdminBase):
    form = InstitucionAdminForm
    search_fields = ["denominacion", "abreviatura",]

class EmpleadoAdminForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_civil'].queryset = RefDet.objects.filter(refcab__cod_referencia__exact='ESTADO_CIVIL')

class EmpleadoAdmin(ModeloAdminBase):
    form = EmpleadoAdminForm
    search_fields = ["nombre", "apellido", "ci"]

class FormacionAcademicaAdmin(ModeloAdminBase):
    list_display =  _list_display
    search_fields = ("titulo_obtenido", "institucion")    
    # autocomplete_fields = ["empleado",]
    list_filter = ["empleado", ]

class DependenciaPosicionAdminForm(forms.ModelForm):
    class Meta:
        model = DependenciaPosicion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['posicion'].queryset = CargoPuesto.objects.all().filter(activo=True)
        self.fields['dependencia'].queryset = Dependencia.objects.all().filter(activo=True)

class DependenciaPosicionAdmin(admin.ModelAdmin):
    
    form = DependenciaPosicionAdminForm
    readonly_fields = _readonly_fields
    list_display = _list_display
    search_fields = ["posicion__denominacion", "dependencia__nombre"]
    autocomplete_fields = ["posicion", "dependencia"]

class MatrizSalarialAdminForm(forms.ModelForm):
    class Meta:
        model = MatrizSalarial
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nivel'].queryset = Nivel.objects.all().filter(activo=True)
        self.fields['categoria'].queryset = CategoriaSalarial.objects.all().filter(activo=True)

class MatrizSalarialAdmin(admin.ModelAdmin):
    form = MatrizSalarialAdminForm
    readonly_fields = _readonly_fields
    list_display = _list_display
    search_fields = ["nivel__denominacion", "categoria__denominacion"]
    # autocomplete_fields = ["nivel", "categoria"]
    

admin.site.register(CategoriaSalarial, ModeloAdminBase)
admin.site.register(CategoriaSalarialVigencia, ModeloAdminBase)
admin.site.register(Nivel, ModeloAdminBase)
admin.site.register(MatrizSalarial, MatrizSalarialAdmin)
admin.site.register(CargoPuesto, ModeloAdminBase)
admin.site.register(Institucion, InstitucionAdmin)
admin.site.register(Sede, ModeloAdminBase)
admin.site.register(Dependencia, ModeloAdminBase)
admin.site.register(DependenciaPosicion, ModeloAdminBase)
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(EmpleadoPosicion, ModeloAdminBase)
admin.site.register(FormacionAcademica, FormacionAcademicaAdmin)
# admin.site.register(ExperienciaLaboral, ModeloAdminBase)
admin.site.register(Capacitacion, ModeloAdminBase)
admin.site.register(DocumentoComplementario, ModeloAdminBase)
admin.site.register(HistoricoDisciplinario, ModeloAdminBase)

