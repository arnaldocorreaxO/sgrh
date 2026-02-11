import datetime
from django import forms
from django.utils.safestring import mark_safe
from django.forms.widgets import ClearableFileInput
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import FormacionAcademica, RefDet, Institucion


# Importa aquí tus modelos según tu estructura de apps
# from .models import FormacionAcademica, Institucion, RefDet

class FormacionAcademicaForm(ModelFormEmpleado):    
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)        
        
        # 1. GENERACIÓN DE AÑOS DINÁMICA
        # Se ejecuta cada vez que se instancia el form, garantizando el año actual.
        current_year = datetime.date.today().year
        self.fields['anho_graduacion'].widget.choices = [('', '(Seleccione año)')] + [
            (str(year), str(year)) for year in range(current_year + 1, current_year - 60, -1)
        ]

        # 2. LÓGICA DE INSTITUCIÓN (Soporte para Select2 dinámico)
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

        # 3. QUERYSETS DE REFERENCIAS (Basados en RefDet)
        self.fields["nivel_academico"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="NIVEL_ACADEMICO"
        ).order_by('descripcion')
        
        self.fields["grado_academico"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="GRADO_ACADEMICO"
        ).order_by('descripcion')

        # 4. CONFIGURACIÓN VISUAL DEL ARCHIVO PDF
        if self.instance and self.instance.pk:
            self.fields['archivo_pdf'].required = False
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                # Agregamos el link actual al help_text existente de forma segura
                link_html = mark_safe(
                    f'<div class="mt-2">'
                    f'<span class="text-info">Archivo actual: </span>'
                    f'<a href="{archivo_url}" target="_blank" class="btn btn-sm btn-outline-danger">'
                    f'<i class="fas fa-file-pdf"></i> Ver documento cargado</a>'
                    f'</div>'
                )
                self.fields['archivo_pdf'].help_text = mark_safe(
                    f"{self.fields['archivo_pdf'].help_text} {link_html}"
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
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'nivel_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'grado_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'titulo_obtenido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Licenciado en Administración'}),
            'denominacion_carrera': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Administración de Empresas'}),
            'anho_graduacion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'nivel_academico': '¿Qué nivel de estudios completó?',
            'institucion': 'Institución educativa',
            'grado_academico': 'Grado académico alcanzado',
            'titulo_obtenido': 'Título obtenido (como figura en el diploma)',
            'denominacion_carrera': 'Nombre de la carrera o especialidad',
            'anho_graduacion': 'Año de egreso o graduación',
            'archivo_pdf': 'Certificado o Título en PDF',
        }
        help_texts = {
            'archivo_pdf': 'Formatos permitidos: PDF. Tamaño máximo: 5MB.',
            'titulo_obtenido': 'Indique el título profesional completo.',
        }

    # VALIDACIONES DE ARCHIVO
    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo and hasattr(archivo, 'name'):
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('El archivo debe estar en formato PDF.')
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo es muy pesado. El límite es de 5MB.')
        return archivo

    # LÓGICA DE GUARDADO INTEGRADA
    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                
                # Si el usuario marcó el checkbox de "Eliminar" en el widget
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
# import datetime
# from django.forms.widgets import ClearableFileInput

# # Importaciones locales (ajusta según tu estructura)
# from core.base.forms import readonly_fields
# from core.rrhh.empleado.forms import ModelFormEmpleado
# from core.rrhh.models import FormacionAcademica, RefDet, Institucion

# # Generación de años dinámica
# current_year = datetime.date.today().year
# YEAR_CHOICES = [('', '(Seleccione año)')] + [(str(year), str(year)) for year in range(current_year + 1, current_year - 60, -1)]

# class FormacionAcademicaForm(ModelFormEmpleado):    
#     def __init__(self, *args, **kwargs):        
#         super().__init__(*args, **kwargs)        
        
#         # 1. LÓGICA DE INSTITUCIÓN (Soporte AJAX para Select2)
#         if 'institucion' in self.data:
#             try:
#                 inst_id = int(self.data.get('institucion'))
#                 self.fields["institucion"].queryset = Institucion.objects.filter(id=inst_id)
#             except (ValueError, TypeError):
#                 self.fields["institucion"].queryset = Institucion.objects.none()
#         elif self.instance and self.instance.institucion_id:
#             self.fields["institucion"].queryset = Institucion.objects.filter(id=self.instance.institucion_id)
#         else:
#             self.fields["institucion"].queryset = Institucion.objects.none()

#         # 2. QUERYSETS DE REFERENCIAS (RefDet)
#         self.fields["nivel_academico"].queryset = RefDet.objects.filter(
#             refcab__cod_referencia="NIVEL_ACADEMICO"
#         ).order_by('descripcion')
        
#         self.fields["grado_academico"].queryset = RefDet.objects.filter(
#             refcab__cod_referencia="GRADO_ACADEMICO"
#         ).order_by('descripcion')

#         # 3. CONFIGURACIÓN DE ARCHIVO EN EDICIÓN
#         if self.instance and self.instance.pk:
#             self.fields['archivo_pdf'].required = False
#             if self.instance.archivo_pdf:
#                 archivo_url = self.instance.archivo_pdf.url
#                 self.fields['archivo_pdf'].help_text += (
#                     f'<br><a href="{archivo_url}" target="_blank" class="text-danger">'
#                     f'<i class="fas fa-file-pdf"></i> Ver título actual</a>'
#                 )

#     class Meta:
#         model = FormacionAcademica
#         fields = [
#             'empleado',
#             'nivel_academico',
#             'institucion',
#             'grado_academico',
#             'denominacion_carrera',
#             'titulo_obtenido',
#             'anho_graduacion',
#             'archivo_pdf',
#         ]
#         exclude = readonly_fields
#         widgets = {
#             'empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'nivel_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'grado_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'titulo_obtenido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ingeniero Civil'}),
#             'anho_graduacion': forms.Select(choices=YEAR_CHOICES, attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
#             'denominacion_carrera': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ingeniería en Sistemas'}),
#             'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
#         }
#         labels = {
#             'nivel_academico': 'Nivel Académico',
#             'institucion': 'Institución Educativa',
#             'titulo_obtenido': 'Título Obtenido',
#             'denominacion_carrera': 'Nombre de la Carrera',
#             'anho_graduacion': 'Año de Graduación',
#             'archivo_pdf': 'Certificado/Título (PDF)',
#         }
#         help_texts = {
#             'archivo_pdf': 'Solo archivos PDF. Máximo 5MB.',
#         }

#     def clean_archivo_pdf(self):
#         archivo = self.cleaned_data.get('archivo_pdf')
#         if archivo:
#             if hasattr(archivo, 'name'): # Evitar error si es un valor booleano (False al borrar)
#                 if not archivo.name.lower().endswith('.pdf'):
#                     raise forms.ValidationError('El archivo debe ser un PDF.')
#                 if archivo.size > 5 * 1024 * 1024:
#                     raise forms.ValidationError('El archivo no debe exceder los 5MB.')
#         return archivo

#     def save(self, commit=True):
#         data = {}
#         try:
#             if self.is_valid():
#                 instance = super().save(commit=False)
#                 # Manejar borrado físico del PDF si se marca el checkbox de ClearableFileInput
#                 if self.cleaned_data.get('archivo_pdf') is False:
#                     if instance.archivo_pdf:
#                         instance.archivo_pdf.delete(save=False)
#                     instance.archivo_pdf = None
                
#                 if commit:
#                     instance.save()
#                 data["success"] = instance
#             else:
#                 data["error"] = self.errors
#         except Exception as e:
#             data["error"] = str(e)
#         return data
    
