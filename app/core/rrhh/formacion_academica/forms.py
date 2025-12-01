from django import forms
from django.forms import ModelForm
from core.base.forms import readonly_fields
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import Empleado, FormacionAcademica, RefDet, Institucion
from django.forms.widgets import ClearableFileInput
import datetime

current_year = datetime.date.today().year
YEAR_CHOICES = [(str(year), str(year)) for year in range(current_year, current_year - 51, -1)]

# FORMACION ACADEMICA
class FormacionAcademicaForm(ModelFormEmpleado):    
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)        
        # NIVEL ACADEMICO (RefDet con cod_referencia específico, similar a estado_civil/sexo)
        nivel_academico = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="NIVEL_ACADEMICO"),  # Ajusta "NIVEL_ACADEMICO" al código real en tu DB
            empty_label="(Seleccione un nivel)",
            label="Nivel Académico",
        )
        nivel_academico.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["nivel_academico"] = nivel_academico
        
        # TITULO OBTENIDO (RefDet con cod_referencia específico)
        titulo_obtenido = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="TITULO_ACADEMICO"),  # Ajusta "TITULO_ACADEMICO" al código real en tu DB
            empty_label="(Seleccione un título)",
            label="Título Obtenido",
        )
        titulo_obtenido.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["titulo_obtenido"] = titulo_obtenido
        
        # INSTITUCION (ForeignKey a Institucion, similar a nacionalidad en EmpleadoForm)
        institucion = forms.ModelChoiceField(
            queryset=Institucion.objects.filter(tipo_funcion__cod_referencia='TIPO_FUNCION_INSTITUCION_EDUCATIVA'),  # Filtrar solo instituciones educativas
            empty_label="(Seleccione una institución)",
            label="Institución",
        )
        institucion.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["institucion"] = institucion

        anho_graduacion = forms.ChoiceField(
        choices=YEAR_CHOICES,
                            widget=forms.Select(attrs={
                                'class': 'form-control select2',
                                'style': 'width: 100%;'
                            })
        )
        self.fields["anho_graduacion"] = anho_graduacion
        
        # Configuración dinámica para campos si hay instancia (similar a ciudad en EmpleadoForm)
        if self.instance:
            # Restaurar querysets si es edición (ejemplo: filtrar por empleado si aplica, pero aquí no)
            self.fields["nivel_academico"].queryset = RefDet.objects.filter(
                refcab__cod_referencia__exact="NIVEL_ACADEMICO"
            ).order_by('descripcion')  # Ordenar por descripción para mejor UX
            self.fields["titulo_obtenido"].queryset = RefDet.objects.filter(
                refcab__cod_referencia__exact="TITULO_ACADEMICO"
            ).order_by('descripcion')
            # self.fields["institucion"].queryset = institucion  # Asumir campo 'nombre'
            
            # No requerir archivo en ediciones si ya existe (mejora del form original)
            self.fields['archivo_pdf'].required = False

            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'

    
    class Meta:
        model = FormacionAcademica
        fields = [
            'empleado',
            'nivel_academico',
            'institucion',
            'titulo_obtenido',
            'denominacion_carrera',
            'anho_graduacion',
            'archivo_pdf',
        ]
        exclude = readonly_fields  # Reutilizar exclude de base si aplica (ajusta si hay campos readonly en este modelo)
        widgets = {
            'nivel_academico': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'titulo_obtenido': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),

        }
        labels = {
            'nivel_academico': 'Nivel Académico',
            'institucion': 'Institución',
            'titulo_obtenido': 'Título Obtenido',
            'denominacion_carrera': 'Carrera',
            'anho_graduacion': 'Año de Graduación',
            'archivo_pdf': 'Archivo PDF (solo PDF)',
        }
        help_texts = {
            'denominacion_carrera': 'Nombre de la carrera (opcional).',
            'archivo_pdf': 'Solo se permiten archivos PDF. Máximo 5MB.',
            'anho_graduacion': 'Año en que se obtuvo el título (opcional).',
        }
    
    # Campo extra para imagen si se necesita en el futuro (reutilizado patrón de EmpleadoForm)
    # image = forms.ImageField(...)  # Descomenta si aplica
    
    def clean_archivo_pdf(self):
        """
        Validación personalizada para archivo PDF, similar a validaciones implícitas en EmpleadoForm.
        """
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('El archivo debe ser un PDF.')
            if archivo.size > 5 * 1024 * 1024:  # Límite de 5MB
                raise forms.ValidationError('El archivo no debe exceder 5MB.')
        return archivo
    
    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                # Si se marcó para limpiar el archivo
                if self.cleaned_data.get('archivo_pdf') is False:
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
   
    # def save_with_empleado(self, commit=True, empleado=None):
    #     data = {}
    #     try:
    #         if self.is_valid():
    #             instance = super().save(commit=False)
    #             if empleado and not instance.pk:
    #                 instance.empleado = empleado
    #             if commit:
    #                 instance.save()
    #             data["success"] = instance
    #         else:
    #             data["error"] = self.errors
    #     except Exception as e:
    #         data["error"] = str(e)
    #     return data
