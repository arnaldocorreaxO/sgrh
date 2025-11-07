from django import forms
from django.forms import ModelForm
from django.core.validators import FileExtensionValidator
from core.base.forms import readonly_fields
from core.rrhh.models import Capacitacion, RefDet, Institucion, Empleado
from django.forms.widgets import ClearableFileInput

class CapacitacionForm(ModelForm):
    """
    Formulario para registrar y editar capacitaciones realizadas por empleados.
    Reutiliza patrones de FormacionForm para consistencia en widgets, validaciones
    y métodos de guardado.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('empleado', None)

        # INSTITUCION
        institucion = forms.ModelChoiceField(
            queryset=Institucion.objects.all(),
            empty_label="(Seleccione una institución)",
            label="Institución",
        )
        institucion.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["institucion"] = institucion

        # TIPO DE CERTIFICACIÓN
        tipo_certificacion = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="TIPO_CERTIFICACION"),
            empty_label="(Seleccione un tipo)",
            label="Tipo de Certificación",
            required=False
        )
        tipo_certificacion.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["tipo_certificacion"] = tipo_certificacion

        # Configuración dinámica si hay instancia
        if self.instance:
            self.fields["institucion"].queryset = Institucion.objects.all().order_by('denominacion')
            self.fields["tipo_certificacion"].queryset = RefDet.objects.filter(
                refcab__cod_referencia__exact="TIPO_CERTIFICACION"
            ).order_by('descripcion')

            self.fields['archivo_pdf'].required = False
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'

    class Meta:
        model = Capacitacion
        exclude = readonly_fields
        fields = [
            'empleado',
            'institucion',
            'nombre_capacitacion',
            'tipo_certificacion',
            'fecha_inicio',
            'fecha_fin',
            'archivo_pdf',
            'observaciones',
        ]
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'tipo_certificacion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'fecha_inicio': forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'type': 'date',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#fecha_inicio',
                }
            ),
            'fecha_fin': forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'type': 'date',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#fecha_fin',
                }
            ),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'institucion': 'Institución',
            'nombre_capacitacion': 'Nombre del Curso',
            'tipo_certificacion': 'Tipo de Certificación',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'archivo_pdf': 'Archivo PDF (solo PDF)',
            'observaciones': 'Observaciones',
        }
        help_texts = {
            'archivo_pdf': 'Solo se permiten archivos PDF. Máximo 5MB.',
            'fecha_inicio': 'Fecha en que inició la capacitación.',
            'fecha_fin': 'Fecha en que finalizó la capacitación.',
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('El archivo debe ser un PDF.')
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no debe exceder 5MB.')
        return archivo

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
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

    def save_with_empleado(self, commit=True, empleado=None):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if empleado and not instance.pk:
                    instance.empleado = empleado
                if commit:
                    instance.save()
                data["success"] = instance
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data
