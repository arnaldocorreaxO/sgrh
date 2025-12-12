from django import forms
from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput
from core.base.forms import readonly_fields
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import DocumentoComplementario, RefDet, Empleado
from django.core.exceptions import ValidationError

class DocumentoComplementarioForm(ModelFormEmpleado):
    """
    Formulario para registrar y editar documentos complementarios de empleados.
    Reutiliza patrones institucionales para consistencia en widgets, validaciones
    y métodos de guardado.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TIPO DE DOCUMENTO
        tipo_documento = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia="TIPO_DOCUMENTO_COMPLEMENTARIO"),
            empty_label="(Seleccione un tipo)",
            label="Tipo de Documento"
        )
        tipo_documento.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["tipo_documento"] = tipo_documento

        # ESTADO DEL DOCUMENTO
        estado_documento = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia="ESTADO_DOCUMENTO_COMPLEMENTARIO"),
            empty_label="(Seleccione un estado)",
            label="Estado del Documento"
        )
        estado_documento.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["estado_documento_empleado"] = estado_documento

        # Configuración dinámica si hay instancia
        if self.instance:
            self.fields["tipo_documento"].queryset = RefDet.objects.filter(
                refcab__cod_referencia="TIPO_DOCUMENTO_COMPLEMENTARIO"
            ).order_by('descripcion')

            self.fields["estado_documento_empleado"].queryset = RefDet.objects.filter(
                refcab__cod_referencia="ESTADO_DOCUMENTO_COMPLEMENTARIO"
            ).order_by('descripcion')

            self.fields['archivo_pdf'].required = False
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'

    class Meta:
        model = DocumentoComplementario
        exclude = readonly_fields
        fields = [
            'empleado',
            'tipo_documento',
            'descripcion',
            'archivo_pdf',
            'estado_documento_empleado',
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'estado_documento_empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'descripcion': 'Descripción',
            'archivo_pdf': 'Archivo PDF (solo PDF)',
            'estado_documento_empleado': 'Estado del Documento',
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
