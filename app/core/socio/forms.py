from django import forms
from django.forms import ModelForm

from core.base.forms import readonly_fields
from core.base.models import RefDet

from .models import *


class SocioForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nro_socio"].widget.attrs["autofocus"] = True
        # super(MovimientoEntradaForm, self).__init__(*args, **kwargs)
        estado_socio = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod__exact="ESTADO_SOCIO"),
            to_field_name="cod",
            empty_label="(Ninguno)",
        )
        estado_socio.widget.attrs.update({"class": "form-control select2"})
        self.fields["estado_socio"] = estado_socio

    class Meta:
        model = Socio
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "sucursal": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "nro_socio": forms.TextInput(attrs={"placeholder": "Nro. Socio"}),
            "persona": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "fec_ingreso": forms.TextInput(
                attrs={"placeholder": "Ingrese Fecha de Charla"}
            ),
            "fec_retiro": forms.TextInput(
                attrs={"placeholder": "Ingrese Fecha de Charla"}
            ),
            "calificacion": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data


class SolicitudIngresoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fec_solicitud"].widget.attrs["autofocus"] = True

    class Meta:
        model = SolicitudIngreso
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "nro_solicitud": forms.TextInput(
                attrs={"placeholder": "Genera Automático"}
            ),
            "fec_solicitud": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_solicitud",
                    "value": datetime.now().strftime("%Y-%m-%d"),
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_solicitud",
                },
            ),
            "fec_charla": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_charla",
                    "value": datetime.now().strftime("%Y-%m-%d"),
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_charla",
                },
            ),
            "sucursal": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "persona": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Indique un Nro. de Telefono para Contacto"}
            ),
            "socio_proponente": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "promocion": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data


class AprobarSolicitudIngresoForm(ModelForm):
    fec_resolucion = forms.DateField(
        label="Fecha de Resolución/Ingreso",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fec_resolucion",
                "value": datetime.now().strftime("%Y-%m-%d"),
                "data-toggle": "datetimepicker",
                "data-target": "#fec_resolucion",
            },
        ),
    )
    ci = forms.CharField(label="CI")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fec_solicitud"].widget.attrs["autofocus"] = True
        if not self.instance.nro_socio:
            self.initial["nro_socio"] = 0
        # Acceso a otros campos Foreign Key del ModelForm
        persona = self.instance.persona
        self.initial["ci"] = persona.ci
        self.fields["ci"].widget.attrs["readonly"] = True

    class Meta:
        model = SolicitudIngreso
        fields = (
            "nro_solicitud",
            "fec_solicitud",
            "fec_charla",
            "persona",
            "autorizado_por",
            "nro_acta",
            "nro_socio",
            "aprobado",
            "motivo_rechazo",
            "activo",
            "persona",
        )

        exclude = readonly_fields
        widgets = {
            "nro_solicitud": forms.TextInput(
                attrs={
                    "readonly": True,
                }
            ),
            "fec_solicitud": forms.TextInput(
                attrs={
                    "readonly": True,
                }
            ),
            "fec_charla": forms.TextInput(
                attrs={
                    "readonly": True,
                }
            ),
            # 'fec_resolucion': forms.DateInput(format='%d-%m-%Y', attrs={
            #     'class': 'form-control datetimepicker-input',
            #     'id': 'fec_resolucion',
            #     'value': datetime.now().strftime('%Y-%m-%d'),
            #     'data-toggle': 'datetimepicker',
            #     'data-target': '#fec_resolucion'
            # }),
            "sucursal": forms.Select(
                attrs={
                    "class": "form-control select2",
                    "style": "width: 100%;",
                    "disabled": True,
                }
            ),
            "persona": forms.Select(
                attrs={
                    "class": "form-control select2",
                    "style": "width: 100%;",
                    "disabled": True,
                }
            ),
            "motivo_rechazo": forms.Textarea(
                attrs={
                    "placeholder": "Indicar Motivo del Rechazo",
                    "rows": 3,
                    "cols": "3",
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data
