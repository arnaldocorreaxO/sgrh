from django.contrib import admin
from django import forms


# Register your models here.
from core.base.admin import ModeloAdminBase
from core.rrhh.models import *
from core.base.admin import _list_display,_readonly_fields
from django.contrib.admin import SimpleListFilter

# Institucion Admin
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


class EmpleadoAdmin(ModeloAdminBase):
    list_display =  _list_display
    search_fields = ("nombre", "apellido", "ci")    
    autocomplete_fields = ["estado_civil",]
    def get_queryset(self, request):
        return Empleado.objects.para_usuario(request.user)

# Formacion Academica Admin
class FormacionAcademicaAdmin(ModeloAdminBase):
    list_display =  _list_display
    search_fields = ("titulo_obtenido", "institucion")    
    autocomplete_fields = ["empleado",]
    list_filter = ["empleado", ]

# Cargo Puesto Admin
class CargoPuestoAdminForm(forms.ModelForm):
    class Meta:
        model = CargoPuesto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matriz_salarial'].queryset = MatrizSalarial.objects.all().filter(activo=True)

class CargoPuestoAdmin(ModeloAdminBase):
    form = CargoPuestoAdminForm
    search_fields = ["denominacion","matriz_salarial__categoria__codigo", "matriz_salarial__denominacion"]
    autocomplete_fields = ["matriz_salarial"]

# Dependencia Admin
class DependenciaAdminForm(forms.ModelForm):
    class Meta:
        model = Dependencia
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sede'].queryset = Sede.objects.all().filter(activo=True)

class DependenciaAdmin(ModeloAdminBase):
    form = DependenciaAdminForm
    search_fields = ["codigo","denominacion", "sede__denominacion"]

# Categoria Salarial Admin
class CategoriaSalarialAdminForm(forms.ModelForm):
    class Meta:
        model = CategoriaSalarial
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vigencias'].queryset = CategoriaSalarialVigencia.objects.all().filter(activo=True)

class CategoriaSalarialAdmin(admin.ModelAdmin):
    form = CategoriaSalarialAdminForm
    readonly_fields = _readonly_fields
    list_display = _list_display
    search_fields = ["codigo","denominacion"]

# Nivel Admin
class NivelAdminForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria_salarial'].queryset = CategoriaSalarial.objects.all().filter(activo=True)

class NivelAdmin(admin.ModelAdmin):
    form = NivelAdminForm
    readonly_fields = _readonly_fields
    list_display = _list_display
    search_fields = ["denominacion", "categoria_salarial__denominacion"]
    # autocomplete_fields = ["categoria_salarial"]

# Matriz Salarial Admin
class MatrizSalarialAdminForm(forms.ModelForm):
    class Meta:
        model = MatrizSalarial
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nivel'].queryset = Nivel.objects.all().filter(activo=True)
        self.fields['categoria'].queryset = CategoriaSalarial.objects.all().filter(activo=True)

class MatrizSalarialAdmin(ModeloAdminBase):
    form = MatrizSalarialAdminForm
    list_filter = ["nivel", "categoria"]
    search_fields = ["nivel__denominacion", "categoria__denominacion","denominacion"]
    autocomplete_fields = ["nivel", "categoria"]

# Dependencia Posicion Admin
class DependenciaPosicionAdminForm(forms.ModelForm):
    class Meta:
        model = DependenciaPosicion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['posicion'].queryset = CargoPuesto.objects.all().filter(activo=True)
        self.fields['dependencia'].queryset = Dependencia.objects.all().filter(activo=True)

class DependenciaPosicionAdmin(ModeloAdminBase):    
    form = DependenciaPosicionAdminForm
    search_fields = ["posicion__denominacion", "dependencia__denominacion"]
    autocomplete_fields = ["posicion","dependencia"]
    
# Empleado Admin
class EmpleadoAdminForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_civil'].queryset = RefDet.objects.filter(refcab__cod_referencia__exact='ESTADO_CIVIL')
        # XO
#Empleado Posicion Admin
class EmpleadoPosicionAdminForm(forms.ModelForm):
    class Meta:
        model = EmpleadoPosicion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['empleado'].queryset = Empleado.objects.all().filter(activo=True)
        self.fields['dependencia_posicion'].queryset = DependenciaPosicion.objects.all().filter(activo=True)
        self.fields['vinculo_laboral'].queryset = RefDet.objects.filter(refcab__cod_referencia__exact='VINCULO_LABORAL')
        self.fields['tipo_movimiento'].queryset = RefDet.objects.filter(refcab__cod_referencia__exact='TIPO_MOVIMIENTO_EMPLEADO_POSICION')

class EmpleadoPosicionAdmin(ModeloAdminBase):    
    form = EmpleadoPosicionAdminForm
    search_fields = ["empleado__nombre", "empleado__apellido"]
    autocomplete_fields = ["empleado","dependencia_posicion"]



# Para que funcione el autocomplete_fields debe registrarse search_fields en el admin correspondiente en cada modelo foreign key
# Ejemplo: CategoriaSalarialAdmin, NivelAdmin, MatrizSalarialAdmin
# Estos deben estar registrados ejemplo CargoPuestoAdmin y DependenciaPosicionAdmin en el admin.site.register

# REGISTRO DE MODELOS
admin.site.register(CategoriaSalarial, CategoriaSalarialAdmin)
admin.site.register(CategoriaSalarialVigencia, CategoriaSalarialAdmin)
admin.site.register(Nivel, NivelAdmin)
admin.site.register(MatrizSalarial, MatrizSalarialAdmin)
admin.site.register(CargoPuesto, CargoPuestoAdmin)
admin.site.register(Institucion, InstitucionAdmin)
admin.site.register(Sede, ModeloAdminBase)
admin.site.register(Dependencia, DependenciaAdmin)
admin.site.register(DependenciaPosicion, DependenciaPosicionAdmin)
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(EmpleadoPosicion, EmpleadoPosicionAdmin)
admin.site.register(FormacionAcademica, FormacionAcademicaAdmin)
# admin.site.register(ExperienciaLaboral, ModeloAdminBase)
admin.site.register(Capacitacion, ModeloAdminBase)
admin.site.register(DocumentoComplementario, ModeloAdminBase)
admin.site.register(HistoricoDisciplinario, ModeloAdminBase)

