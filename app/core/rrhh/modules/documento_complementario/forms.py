from django import forms
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError

from core.base.forms import readonly_fields
from core.rrhh.modules.empleado.forms import ModelFormEmpleado
from core.rrhh.models import DocumentoComplementario, RefDet

# FORMULARIO FILTRO EMPLEADO
class DocumentoComplementarioFilterForm(forms.Form):

    tipo_documento = forms.ModelChoiceField(
        queryset=RefDet.objects.filter(refcab__cod_referencia="TIPO_DOCUMENTO_COMPLEMENTARIO").order_by('descripcion'),
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "style": "width: 100%;",
            "id": "id_tipo_documento",
        })
    )   

    rango_fecha = forms.CharField(
        label="Rango de Fechas",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione periodo...',
            'autocomplete': 'off',
            'id': 'id_rango_fecha' # Forzamos el ID para el JS
        }),
        required=False
    )
    

class DocumentoComplementarioForm(ModelFormEmpleado):
    """
    Formulario optimizado para documentos complementarios.
    Hereda la gestión de 'empleado' de ModelFormEmpleado.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. QUERYSETS DINÁMICOS (RefDet)
        # Asignamos el queryset a los campos ya definidos en el Meta
        self.fields["tipo_documento"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_DOCUMENTO_COMPLEMENTARIO"
        ).order_by('descripcion')

        self.fields["estado_documento_empleado"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="ESTADO_DOCUMENTO_COMPLEMENTARIO"
        ).order_by('descripcion')

        # 2. GESTIÓN DE ARCHIVO EN EDICIÓN
        if self.instance and self.instance.pk:
            self.fields['archivo_pdf'].required = False
            
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                self.fields['archivo_pdf'].help_text += (
                    f'<br><a href="{archivo_url}" target="_blank" class="text-primary">'
                    f'<i class="fas fa-file-pdf"></i> Ver documento actual</a>'
                )

    class Meta:
        model = DocumentoComplementario
        exclude = readonly_fields
        fields = [
            'empleado',
            'fecha_documento',
            'tipo_documento',
            'descripcion',
            'archivo_pdf',
            'estado_documento_empleado',
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'estado_documento_empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Breve detalle del documento...'}),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
            'fecha_documento': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }
        labels = {
            'tipo_documento': 'Categoría de Documento',
            'descripcion': 'Observaciones / Descripción',
            'archivo_pdf': 'Documento Digital (PDF)',
            'estado_documento_empleado': 'Estado Actual',
        }
        help_texts = {
            'archivo_pdf': 'Formato PDF obligatorio. Máximo 5MB.',
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo and hasattr(archivo, 'name'):
            # Validar extensión
            if not archivo.name.lower().endswith('.pdf'):
                raise ValidationError('El archivo debe ser un PDF.')
            # Validar tamaño
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no debe exceder los 5MB.')
        return archivo

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                # Si se marcó "Eliminar" en el widget Clearable
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