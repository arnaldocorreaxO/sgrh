from django import forms
from django.forms import ModelForm

from core.base.forms import readonly_fields
from core.base.models import RefDet

from .models import *


class SolicitudPrestamoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fec_solicitud"].widget.attrs["autofocus"] = True

    class Meta:
        model = SolicitudPrestamo
        fields = "__all__"
        exclude = readonly_fields
        # widgets = {
        #     "nro_solicitud": forms.TextInput(
        #         attrs={"placeholder": "Genera Automático"}
        #     ),
        #     "fec_solicitud": forms.DateInput(
        #         format="%Y-%m-%d",
        #         attrs={
        #             "class": "form-control datetimepicker-input",
        #             "id": "fec_solicitud",
        #             "value": datetime.now().strftime("%Y-%m-%d"),
        #             "data-toggle": "datetimepicker",
        #             "data-target": "#fec_solicitud",
        #         },
        #     ),
        #     "fec_charla": forms.DateInput(
        #         format="%Y-%m-%d",
        #         attrs={
        #             "class": "form-control datetimepicker-input",
        #             "id": "fec_charla",
        #             "value": datetime.now().strftime("%Y-%m-%d"),
        #             "data-toggle": "datetimepicker",
        #             "data-target": "#fec_charla",
        #         },
        #     ),
        #     "sucursal": forms.Select(
        #         attrs={"class": "form-control select2", "style": "width: 100%;"}
        #     ),
        #     "persona": forms.Select(
        #         attrs={"class": "form-control select2", "style": "width: 100%;"}
        #     ),
        #     "telefono": forms.TextInput(
        #         attrs={"placeholder": "Ingrese Nro. de Telefono"}
        #     ),
        #     "socio_proponente": forms.Select(
        #         attrs={"class": "form-control select2", "style": "width: 100%;"}
        #     ),
        #     "promocion": forms.Select(
        #         attrs={"class": "form-control select2", "style": "width: 100%;"}
        #     ),
        # }

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
