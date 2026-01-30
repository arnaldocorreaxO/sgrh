from django import forms
from django.forms import ModelForm
from django.core.validators import FileExtensionValidator
from core.base.forms import readonly_fields
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import Capacitacion, RefDet, Institucion, Empleado
from django.forms.widgets import ClearableFileInput

class CapacitacionForm(ModelFormEmpleado):
    """
    Formulario para registrar y editar capacitaciones realizadas por empleados.
    Hereda de ModelFormEmpleado la validación dinámica del campo 'empleado'.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- LÓGICA PARA CAMPO INSTITUCIÓN (Rehidratación para AJAX) ---
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

        # --- TIPO DE CERTIFICACIÓN (RefDet) ---
        # Solo asignamos el queryset al campo ya definido en Meta
        self.fields["tipo_certificacion"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_CERTIFICACION"
        ).order_by('descripcion')

        # --- CONFIGURACIÓN DE ARCHIVO PDF ---
        if self.instance and self.instance.pk:
            # No es obligatorio subir el archivo de nuevo al editar
            self.fields['archivo_pdf'].required = False
            
            if self.instance.archivo_pdf:
                archivo_url = self.instance.archivo_pdf.url
                # Agregamos link de descarga al texto de ayuda
                self.fields['archivo_pdf'].help_text += f'<br><a href="{archivo_url}" target="_blank" class="text-primary"><i class="fas fa-file-pdf"></i> Ver archivo actual</a>'

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
            'empleado': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'institucion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'tipo_certificacion': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'fecha_inicio': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fecha_fin': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'institucion': 'Institución',
            'nombre_capacitacion': 'Nombre del Curso / Capacitación',
            'tipo_certificacion': 'Tipo de Certificación',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'archivo_pdf': 'Archivo de Certificado (PDF)',
            'observaciones': 'Observaciones adicionales',
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('El archivo debe ser un formato PDF válido.')
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El tamaño del archivo no debe exceder los 5MB.')
        return archivo

    def clean(self):
        """Validación cruzada de fechas"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError({
                    'fecha_fin': "La fecha de finalización no puede ser anterior a la fecha de inicio."
                })
        return cleaned_data

    # El método save() se hereda o se mantiene igual según tu lógica de retorno de diccionarios.

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
