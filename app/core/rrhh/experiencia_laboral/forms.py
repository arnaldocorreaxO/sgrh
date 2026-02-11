from django import forms
from django.forms import ClearableFileInput

from core.base.models import RefCab
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import ExperienciaLaboral, Institucion, RefDet
from core.base.forms import readonly_fields
from django.core.exceptions import ValidationError

class CargoChoiceField(forms.ModelChoiceField):
    """
    Campo personalizado que permite valores tipo 'new:XYZ'
    sin que Django los rechace antes de clean_cargo().
    """
    def validate(self, value):
        # Permitir valores nuevos creados por Select2
        if isinstance(value, str) and value.startswith("new:"):
            return
        super().validate(value)


from django import forms
from django.utils.safestring import mark_safe

class ExperienciaLaboralForm(ModelFormEmpleado):

    empresa = forms.CharField(
        label="Empresa donde trabajó",
        help_text="Si no existe en la lista, escríbala y presione Enter para crearla.",
        widget=forms.Select(
            attrs={
                "class": "custom-select select2",
                "style": "width: 100%",
                "data-placeholder": "Seleccione o escriba una empresa",
            }
        ),
        required=True,
    )

    cargo = forms.CharField(
        label="Cargo desempeñado",
        help_text="Si no existe en la lista, escríbalo y presione Enter para crearlo.",
        widget=forms.Select(
            attrs={
                "class": "custom-select select2",
                "style": "width: 100%",
                "data-placeholder": "Seleccione o escriba un cargo",
            }
        ),
        required=True,
    )

    actividades = forms.CharField(
        label="Actividades o tareas",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "3",
                "placeholder": "Ej: Gestión de inventarios, atención al cliente, elaboración de informes...",
            }
        ),
        help_text="Mencione brevemente sus tareas principales o deje en blanco si no desea detallar."
    )
    archivo_pdf = forms.FileField(
        label="Respaldo de experiencia",
        required=False,
        help_text="Puede adjuntar un certificado o constancia laboral en PDF (opcional).",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance if self.instance and self.instance.pk else None

        # --- Configuración de Empresa ---
        self.fields["empresa"].widget.choices = []
        if inst and inst.empresa:
            self.initial["empresa"] = inst.empresa.pk
            self.fields["empresa"].widget.choices = [(inst.empresa.pk, inst.empresa.denominacion)]

        # --- Configuración de Cargo ---
        self.fields["cargo"].widget.choices = []
        if inst and inst.cargo:
            self.initial["cargo"] = inst.cargo.pk
            self.fields["cargo"].widget.choices = [(inst.cargo.pk, inst.cargo.denominacion)]

        # --- Archivo PDF ---
        self.fields["archivo_pdf"].required = False
        if inst and inst.archivo_pdf:
                # Mantenemos el texto de ayuda original y agregamos el link al actual
                self.fields["archivo_pdf"].help_text = mark_safe(
                    f'Puede reemplazar el documento actual subiendo uno nuevo en PDF.<br>'
                    f'<span class="text-success"><i class="fa fa-check-circle"></i> Archivo ya cargado: '
                    f'<a href="{inst.archivo_pdf.url}" target="_blank" class="font-weight-bold">Ver documento</a></span>'
                )

    class Meta:
        model = ExperienciaLaboral
        fields = [
            'empleado',
            'empresa',
            'cargo',
            'fecha_desde',
            'fecha_hasta',
            'actividades',
            'archivo_pdf',
        ]
        widgets = {
            'fecha_desde': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fecha_hasta': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'archivo_pdf': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_empresa(self):
        raw = self.data.get("empresa", "")
        print(">>> clean_empresa() recibió:", raw)

        if not raw:
            return None

        # caso nuevo: new:XYZ
        if raw.startswith("new:"):
            descripcion = raw.replace("new:", "").strip()
            print(">>> creando nueva empresa:", descripcion)

            empresa = RefDet.objects.create(
                refcab=RefCab.objects.get(cod_referencia="EMPRESA"),
                denominacion=descripcion,
                descripcion=descripcion,
            )
            empresa.cod_referencia = f"EMPRESA_{empresa.pk}"
            empresa.save(update_fields=['cod_referencia'])
            return empresa

        # caso existente: viene un pk (string) desde Select2
        try:
            empresa = RefDet.objects.get(pk=raw)
            return empresa
        except RefDet.DoesNotExist:
            raise ValidationError("Escoja una empresa válida.")
        
    # ---------------------------------------------------------
    # CREACIÓN DINÁMICA DE CARGO
    # ---------------------------------------------------------
    def clean_cargo(self):
            raw = self.data.get("cargo", "")
            print(">>> clean_cargo() recibió:", raw)

            if not raw:
                return None

            # caso nuevo: new:XYZ
            if raw.startswith("new:"):
                descripcion = raw.replace("new:", "").strip()
                print(">>> creando nuevo cargo:", descripcion)

                cargo = RefDet.objects.create(
                    refcab=RefCab.objects.get(cod_referencia="CARGO"),
                    denominacion=descripcion,
                    descripcion=descripcion,
                )
                cargo.cod_referencia = f"CARGO_{cargo.pk}"
                cargo.save(update_fields=['cod_referencia'])
                return cargo

            # caso existente: viene un pk (string) desde Select2
            try:
                cargo = RefDet.objects.get(pk=raw)
                return cargo
            except RefDet.DoesNotExist:
                raise ValidationError("Escoja un cargo válido.")


    # ---------------------------------------------------------
    # VALIDACIÓN PDF
    # ---------------------------------------------------------
    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise ValidationError('El archivo debe ser un PDF.')
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no debe exceder 5MB.')
        return archivo

    # ---------------------------------------------------------
    # SAVE INSTITUCIONAL
    # ---------------------------------------------------------
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