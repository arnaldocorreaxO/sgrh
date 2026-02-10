from django import forms
import datetime
from django.forms.widgets import ClearableFileInput

# Importaciones locales (ajusta según tu estructura)
from core.base.forms import readonly_fields
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import FormacionAcademica, RefDet, Institucion

# Generación de años dinámica
current_year = datetime.date.today().year
YEAR_CHOICES = [('', '(Seleccione año)')] + [(str(year), str(year)) for year in range(current_year + 1, current_year - 60, -1)]

class FormacionAcademicaForm(ModelFormEmpleado):    
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)        
        
        # 1. LÓGICA DE INSTITUCIÓN (Soporte AJAX para Select2)
        if 'institucion' in self.data:
            try:
                inst_id = int(self.data.get('institucion'))
                self.fields["institucion"].queryset = Institucion.objects.filter(id=inst_id)
            except (ValueError, TypeError):
                self.fields["institucion"].queryset = Institucion.objects.none()
        elif self.instance and self.instance.institucion_id:
            self.fields["institucion"].queryset = Institucion.objects.filter(id=self.instance.institucion_id)
        else:
            self.fields["institucion"].queryset = Institucion.objects.none()

        # 2. QUERYSETS DE REFERENCIAS (RefDet)
        self.fields["nivel_academico"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="NIVEL_ACADEMICO"
        ).order_by('descripcion')
        
        self.fields["grado_academico"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="GRADO_ACADEMICO"
        ).order_by('descripcion')

        # 3. CONFIGURACIÓN DE ARCHIVO EN EDICIÓN
        if self.instance and self.instance.pk:
            self.fields['archivo_pdf'].required = False
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                self.fields['archivo_pdf'].help_text += (
                    f'<br><a href="{archivo_url}" target="_blank" class="text-danger">'
                    f'<i class="fas fa-file-pdf"></i> Ver título actual</a>'
                )

    class Meta:
        model = FormacionAcademica
        fields = [
            'empleado',
            'nivel_academico',
            'institucion',
            'grado_academico',
            'denominacion_carrera',
            'titulo_obtenido',
            'anho_graduacion',
            'archivo_pdf',
        ]
        exclude = readonly_fields
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'nivel_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'grado_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'titulo_obtenido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ingeniero Civil'}),
            'anho_graduacion': forms.Select(choices=YEAR_CHOICES, attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'denominacion_carrera': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ingeniería en Sistemas'}),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'nivel_academico': 'Nivel Académico',
            'institucion': 'Institución Educativa',
            'titulo_obtenido': 'Título Obtenido',
            'denominacion_carrera': 'Nombre de la Carrera',
            'anho_graduacion': 'Año de Graduación',
            'archivo_pdf': 'Certificado/Título (PDF)',
        }
        help_texts = {
            'archivo_pdf': 'Solo archivos PDF. Máximo 5MB.',
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if hasattr(archivo, 'name'): # Evitar error si es un valor booleano (False al borrar)
                if not archivo.name.lower().endswith('.pdf'):
                    raise forms.ValidationError('El archivo debe ser un PDF.')
                if archivo.size > 5 * 1024 * 1024:
                    raise forms.ValidationError('El archivo no debe exceder los 5MB.')
        return archivo

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                # Manejar borrado físico del PDF si se marca el checkbox de ClearableFileInput
                if self.cleaned_data.get('archivo_pdf') is False:
                    if instance.archivo_pdf:
                        instance.archivo_pdf.delete(save=False)
                    instance.archivo_pdf = None
                
                if commit:
                    instance.save()
                data["success"] = instance
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data
    
# from django import forms
# from django.forms import ModelForm
# from core.base.forms import readonly_fields
# from core.rrhh.empleado.forms import ModelFormEmpleado
# from core.rrhh.models import Empleado, FormacionAcademica, RefDet, Institucion
# from django.forms.widgets import ClearableFileInput
# import datetime

# current_year = datetime.date.today().year
# YEAR_CHOICES = [(str(year), str(year)) for year in range(current_year, current_year - 51, -1)]

# # FORMACION ACADEMICA
# class FormacionAcademicaForm(ModelFormEmpleado):    
#     def __init__(self, *args, **kwargs):        
#         super().__init__(*args, **kwargs)        
#         # NIVEL ACADEMICO (RefDet con cod_referencia específico, similar a estado_civil/sexo)
#         nivel_academico = forms.ModelChoiceField(
#             queryset=RefDet.objects.filter(refcab__cod_referencia__exact="NIVEL_ACADEMICO"),  # Ajusta "NIVEL_ACADEMICO" al código real en tu DB
#             empty_label="(Seleccione un nivel)",
#             label="Nivel Académico",
#         )
#         nivel_academico.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
#         self.fields["nivel_academico"] = nivel_academico
        
#         # TITULO OBTENIDO (RefDet con cod_referencia específico)
#         titulo_obtenido = forms.ModelChoiceField(
#             queryset=RefDet.objects.filter(refcab__cod_referencia__exact="TITULO_ACADEMICO"),  # Ajusta "TITULO_ACADEMICO" al código real en tu DB
#             empty_label="(Seleccione un título)",
#             label="Título Obtenido",
#         )
#         titulo_obtenido.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
#         self.fields["titulo_obtenido"] = titulo_obtenido
      
#         # Empleado dinamico
#         # Se define en base al contexto ModelFormEmpleado si aplica           
            
#         # --- INSTITUCIÓN ---
#         # 1. Si es una carga inicial (GET) y hay instancia, mostramos solo esa
#         if self.instance and self.instance.institucion_id:
#             self.fields["institucion"].queryset = Institucion.objects.filter(id=self.instance.institucion_id)
#         # 2. SI ES UN POST (envío de datos), debemos permitir que el valor enviado sea válido
#         elif 'institucion' in self.data:
#             try:
#                 institucion_id = int(self.data.get('institucion'))
#                 self.fields["institucion"].queryset = Institucion.objects.filter(id=institucion_id)
#             except (ValueError, TypeError):
#                 self.fields["institucion"].queryset = Institucion.objects.none()
#         # 3. Por defecto (nuevo registro vacío)
#         else:
#             self.fields["institucion"].queryset = Institucion.objects.none()

#         anho_graduacion = forms.ChoiceField(
#         choices=YEAR_CHOICES,
#                             widget=forms.Select(attrs={
#                                 'class': 'form-control select2',
#                                 'style': 'width: 100%;'
#                             })
#         )
#         self.fields["anho_graduacion"] = anho_graduacion
        
#         # Configuración dinámica para campos si hay instancia (similar a ciudad en EmpleadoForm)
#         if self.instance:
#             # Restaurar querysets si es edición (ejemplo: filtrar por empleado si aplica, pero aquí no)
#             self.fields["nivel_academico"].queryset = RefDet.objects.filter(
#                 refcab__cod_referencia__exact="NIVEL_ACADEMICO"
#             ).order_by('descripcion')  # Ordenar por descripción para mejor UX
#             self.fields["titulo_obtenido"].queryset = RefDet.objects.filter(
#                 refcab__cod_referencia__exact="TITULO_ACADEMICO"
#             ).order_by('descripcion')
#             # self.fields["institucion"].queryset = institucion  # Asumir campo 'nombre'
            
#             # No requerir archivo en ediciones si ya existe (mejora del form original)
#             self.fields['archivo_pdf'].required = False

#             if self.instance.archivo_pdf:
#                 archivo_url = self.instance.archivo_pdf.url
#                 self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'

    
#     class Meta:
#         model = FormacionAcademica
#         fields = [
#             'empleado',
#             'nivel_academico',
#             'institucion',
#             'titulo_obtenido',
#             'denominacion_carrera',
#             'anho_graduacion',
#             'archivo_pdf',
#         ]
#         exclude = readonly_fields  # Reutilizar exclude de base si aplica (ajusta si hay campos readonly en este modelo)
#         widgets = {
#             'nivel_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'titulo_obtenido': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),

#         }
#         labels = {
#             'nivel_academico': 'Nivel Académico',
#             'institucion': 'Institución',
#             'titulo_obtenido': 'Título Obtenido',
#             'denominacion_carrera': 'Carrera',
#             'anho_graduacion': 'Año de Graduación',
#             'archivo_pdf': 'Archivo PDF (solo PDF)',
#         }
#         help_texts = {
#             'denominacion_carrera': 'Nombre de la carrera (opcional).',
#             'archivo_pdf': 'Solo se permiten archivos PDF. Máximo 5MB.',
#             'anho_graduacion': 'Año en que se obtuvo el título (opcional).',
#         }
    
#     # Campo extra para imagen si se necesita en el futuro (reutilizado patrón de EmpleadoForm)
#     # image = forms.ImageField(...)  # Descomenta si aplica
    
#     def clean_archivo_pdf(self):
#         """
#         Validación personalizada para archivo PDF, similar a validaciones implícitas en EmpleadoForm.
#         """
#         archivo = self.cleaned_data.get('archivo_pdf')
#         if archivo:
#             if not archivo.name.lower().endswith('.pdf'):
#                 raise forms.ValidationError('El archivo debe ser un PDF.')
#             if archivo.size > 5 * 1024 * 1024:  # Límite de 5MB
#                 raise forms.ValidationError('El archivo no debe exceder 5MB.')
#         return archivo
    
#     def save(self, commit=True):
#         data = {}
#         try:
#             if self.is_valid():
#                 instance = super().save(commit=False)
#                 # Si se marcó para limpiar el archivo
#                 if self.cleaned_data.get('archivo_pdf') is False:
#                     instance.archivo_pdf.delete(save=False)
#                     instance.archivo_pdf = None
#                 if commit:
#                     instance.save()
#                 data["success"] = instance
#             else:
#                 data["error"] = self.errors
#         except Exception as e:
#             data["error"] = str(e)
#         return data