from django import forms
from django.utils.safestring import mark_safe
from django.forms.widgets import ClearableFileInput
from core.base.forms import readonly_fields
from core.rrhh.modules.empleado.forms import ModelFormEmpleado
from core.rrhh.models import Capacitacion, RefDet, Institucion


class CapacitacionForm(ModelFormEmpleado):
    """
    Formulario optimizado para el registro de capacitaciones y cursos.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. LÓGICA PARA CAMPO INSTITUCIÓN (Soporte AJAX para Select2)
        if "institucion" in self.data:
            try:
                inst_id = int(self.data.get("institucion"))
                self.fields["institucion"].queryset = Institucion.objects.filter(
                    id=inst_id
                )
            except (ValueError, TypeError):
                self.fields["institucion"].queryset = Institucion.objects.none()
        elif self.instance and self.instance.institucion_id:
            self.fields["institucion"].queryset = Institucion.objects.filter(
                id=self.instance.institucion_id
            )
        else:
            self.fields["institucion"].queryset = Institucion.objects.none()

        # 2. TIPO DE CERTIFICACIÓN (Carga desde RefDet)
        self.fields["tipo_certificacion"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_CERTIFICACION"
        ).order_by("descripcion")

        # 3. CONFIGURACIÓN VISUAL DEL ARCHIVO PDF (En edición)
        if self.instance and self.instance.pk:
            self.fields["archivo_pdf"].required = False
            # if self.instance.archivo_pdf:
            # archivo_url = self.instance.archivo_pdf.url
            # link_html = mark_safe(
            #     f'<div class="mt-2">'
            #     f'<span class="text-info">Archivo actual: </span>'
            #     f'<a href="{archivo_url}" target="_blank" class="btn btn-sm btn-outline-primary">'
            #     f'<i class="fas fa-file-pdf"></i> Ver certificado cargado</a>'
            #     f"</div>"
            # )
            # # Evitamos duplicar si ya existe help_text
            # self.fields["archivo_pdf"].help_text = mark_safe(f"{link_html}")

    class Meta:
        model = Capacitacion
        exclude = readonly_fields
        fields = [
            "empleado",
            "institucion",
            "nombre_capacitacion",
            "tipo_certificacion",
            "fecha_inicio",
            "fecha_fin",
            "horas_acreditadas",
            "archivo_pdf",
            "observaciones",
        ]
        widgets = {
            "empleado": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "institucion": forms.Select(
                attrs={
                    "class": "form-control select2",
                    "style": "width: 100%;",
                    "data-placeholder": "Seleccione la institución",
                }
            ),
            "tipo_certificacion": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "nombre_capacitacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Curso de Especialización en Gobernanza Pública",
                }
            ),
            "fecha_inicio": forms.DateInput(
                format="%Y-%m-%d", attrs={"class": "form-control", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                format="%Y-%m-%d", attrs={"class": "form-control", "type": "date"}
            ),
            "horas_acreditadas": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese las horas acreditadas (opcional)",
                }
            ),
            "archivo_pdf": ClearableFileInput(attrs={"class": "form-control-file"}),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Breve descripción de los temas abordados (opcional)",
                }
            ),
        }
        labels = {
            "institucion": "¿Dónde realizó la capacitación?",
            "nombre_capacitacion": "Nombre del curso o capacitación",
            "tipo_certificacion": "Tipo de certificado recibido",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de finalización",
            "archivo_pdf": "Certificado en PDF",
            "horas_acreditadas": "Horas acreditadas",
            "observaciones": "Detalles adicionales",
        }
        help_texts = {
            "archivo_pdf": "Cargue el diploma o constancia en PDF (máx. 5MB).",
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get("archivo_pdf")
        if archivo and hasattr(archivo, "name"):
            if not archivo.name.lower().endswith(".pdf"):
                raise forms.ValidationError("El archivo debe estar en formato PDF.")
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El archivo no debe superar los 5MB.")
        return archivo

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    {
                        "fecha_fin": "La fecha de finalización no puede ser anterior a la de inicio."
                    }
                )
        return cleaned_data

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                # Manejo de borrado físico si se usa el widget Clearable
                if self.cleaned_data.get("archivo_pdf") is False:
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
