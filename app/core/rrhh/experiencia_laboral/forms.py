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


class ExperienciaLaboralForm(ModelFormEmpleado):

    # ---------------------------------------------------------
    # 🔥 CAMPO PERSONALIZADO DEFINIDO A NIVEL DE CLASE
    # ---------------------------------------------------------
    
    empresa = forms.CharField(
        label="Empresa donde trabajó",
         widget=forms.Select(
            attrs={

                "class": "custom-select select2",
                "style": "width: 100%",
            }
        ),
        required=False,
    )

    cargo = forms.CharField(
        label="Cargo desempeñado",
         widget=forms.Select(
            attrs={

                "class": "custom-select select2",
                "style": "width: 100%",
            }
        ),
        required=False,
    )
        

    def __init__(self, *args, **kwargs):
        print(">>> instancia del form:", id(self))
        super().__init__(*args, **kwargs)

        # En Experiencia Laboral, el campo empresa y cargo son RefDet no son declarados en el modelo

        # ---------------------------------------------------------
        # EMPRESA (ya declarado arriba)
        # ---------------------------------------------------------

        # Para que Select2 no cargue opciones al abrir
        self.fields["empresa"].widget.choices = []

        # Si estamos editando, cargar solo el cargo actual
        inst = self.instance if self.instance and self.instance.pk else None

        if inst and inst.empresa:
            # valor inicial del campo
            self.initial["empresa"] = inst.empresa.pk

            # opción visible en el select
            self.fields["empresa"].widget.choices = [
            (inst.empresa.pk, inst.empresa.denominacion)
            ]

        # ---------------------------------------------------------
        # CARGO (ya declarado arriba)
        # ---------------------------------------------------------

        # Para que Select2 no cargue opciones al abrir
        self.fields["cargo"].widget.choices = []

        # Si estamos editando, cargar solo el cargo actual
        if inst and inst.cargo:
            # valor inicial del campo
            self.initial["cargo"] = inst.cargo.pk

            # opción visible en el select
            self.fields["cargo"].widget.choices = [
            (inst.cargo.pk, inst.cargo.denominacion)
            ]


        # ---------------------------------------------------------
        # ARCHIVO PDF
        # ---------------------------------------------------------
        self.fields["archivo_pdf"].required = False
        if inst and inst.archivo_pdf:
            archivo_url = inst.archivo_pdf.url
            self.fields["archivo_pdf"].help_text += (
                f'<br><a href="{archivo_url}" target="_blank">Ver archivo actual</a>'
            )

    # ---------------------------------------------------------
    # META
    # ---------------------------------------------------------
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'empleado',
            'empresa',
            'cargo',
            'fecha_desde',
            'fecha_hasta',
            'motivo_retiro',
            'archivo_pdf',
        ]
        widgets = {
            
            # ⚠️ IMPORTANTE: NO DEFINIR WIDGET PARA "empresa" y "cargo"
            'fecha_desde': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fecha_hasta': forms.DateInput(
                format="%Y-%m-%d",
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
            'motivo_retiro': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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