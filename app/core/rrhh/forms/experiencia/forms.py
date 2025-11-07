from django import forms
from django.forms import ModelForm, ClearableFileInput
from django.forms.models import model_to_dict
from core.rrhh.models import ExperienciaLaboral, Institucion, RefDet
from core.base.forms import readonly_fields
from django.core.exceptions import ValidationError

class ExperienciaLaboralForm(ModelForm):
    """
    Formulario para registrar y editar experiencias laborales de empleados.
    Reutiliza patrones de formularios institucionales para consistencia en widgets,
    validaciones y métodos de guardado.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('empleado', None)

        # INSTITUCIÓN
        institucion = forms.ModelChoiceField(
            queryset=Institucion.objects.all(),
            empty_label="(Seleccione una institución)",
            label="Institución",
        )
        institucion.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["institucion"] = institucion

        # CARGO
        cargo = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia="CARGO_PUESTO"),
            empty_label="(Seleccione un cargo)",
            label="Cargo",
        )
        cargo.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["cargo"] = cargo

        # Configuración dinámica si hay instancia
        if self.instance:
            self.fields["institucion"].queryset = Institucion.objects.all().order_by('denominacion')
            self.fields["cargo"].queryset = RefDet.objects.filter(
                refcab__cod_referencia="CARGO_PUESTO"
            ).order_by('descripcion')

            self.fields['archivo_pdf'].required = False
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'

    class Meta:
        model = ExperienciaLaboral
        exclude = readonly_fields
        fields = [
            'empleado',
            'institucion',
            'cargo',
            'fecha_desde',
            'fecha_hasta',
            'motivo_retiro',
            'archivo_pdf',
        ]
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'cargo': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'fecha_desde': forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'type': 'date',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#fecha_desde',
                }
            ),
            'fecha_hasta': forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'type': 'date',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#fecha_hasta',
                }
            ),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
            'motivo_retiro': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'institucion': 'Institución',
            'cargo': 'Cargo desempeñado',
            'fecha_desde': 'Fecha de Inicio',
            'fecha_hasta': 'Fecha de Finalización',
            'archivo_pdf': 'Archivo PDF (solo PDF)',
            'motivo_retiro': 'Motivo del Retiro',
        }
        help_texts = {
            'archivo_pdf': 'Solo se permiten archivos PDF. Máximo 5MB.',
            'fecha_desde': 'Fecha en que inició la experiencia laboral.',
            'fecha_hasta': 'Fecha en que finalizó la experiencia laboral.',
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
