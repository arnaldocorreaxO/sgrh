from django import forms
from django.forms.widgets import ClearableFileInput
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import HistoricoDisciplinario, RefDet
from django.core.exceptions import ValidationError

class HistoricoDisciplinarioForm(ModelFormEmpleado):
    """
    Formulario institucional para documentos disciplinarios.
    Aplica estilos, validaciones y lógica de guardado con asignación dinámica de empleado.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Querysets filtrados y ordenados
        self.fields['tipo_falta'].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_FALTA_DISCIPLINARIA"
        ).order_by('valor_orden')

        # Querysets filtrados y ordenados
        self.fields['tipo_sancion'].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_SANCION_DISCIPLINARIA"
        ).order_by('descripcion')

        # Querysets filtrados y ordenados
        self.fields['tipo_documento'].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_DOCUMENTO"
        ).order_by('descripcion')

        self.fields['estado_documento'].queryset = RefDet.objects.filter(
            refcab__cod_referencia="ESTADO_DOCUMENTO"
        ).order_by('descripcion')

        # Archivo PDF opcional si ya existe
        self.fields['archivo_pdf'].required = False
        if self.instance and self.instance.archivo_pdf:
            archivo_url = self.instance.archivo_pdf.url
            self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'

    class Meta:
        model = HistoricoDisciplinario
        fields = [
            'empleado',
            'tipo_falta',
            'tipo_sancion',
            'tipo_documento',
            'descripcion',
            'fecha_emision',
            'institucion_emisora',
            'archivo_pdf',
            'estado_documento',
        ]
        widgets = {
            'tipo_falta': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'tipo_sancion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'estado_documento': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'institucion_emisora': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'empleado': 'Empleado',
            'tipo_falta': 'Tipo de Falta',
            'tipo_sancion': 'Tipo de Sanción',
            'tipo_documento': 'Tipo de Documento',
            'descripcion': 'Descripción',
            'fecha_emision': 'Fecha de Emisión',
            'institucion_emisora': 'Institución Emisora',
            'archivo_pdf': 'Archivo PDF',
            'estado_documento': 'Estado del Documento',
        }
        help_texts = {
            'archivo_pdf': 'Solo se permiten archivos PDF. Máximo 5MB.',
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise ValidationError('El archivo debe ser un PDF.')
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no debe exceder 5MB.')
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
