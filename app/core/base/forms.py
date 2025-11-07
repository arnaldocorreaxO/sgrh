from django import forms
from django.forms import ModelForm

from core.base.utils import get_fecha_actual, get_fecha_actual_ymd

from .models import *

# Campo de solo lectura para todos los forms
readonly_fields = [
    "usu_insercion",
    "fec_insercion",
    "usu_modificacion",
    "fec_modificacion",
]


class EmpresaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["denominacion"].widget.attrs["autofocus"] = True
        for form in self.visible_fields():
            form.field.widget.attrs.update(
                {"class": "form-control", "autocomplete": "off"}
            )

    class Meta:
        model = Empresa
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "denominacion": forms.TextInput(attrs={"placeholder": "Ingrese un nombre"}),
            "ruc": forms.TextInput(attrs={"placeholder": "Ingrese un ruc"}),
            "celular": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono celular"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono convencional"}
            ),
            "email": forms.TextInput(attrs={"placeholder": "Ingrese un email"}),
            "direccion": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección"}
            ),
            "website": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección web"}
            ),
            "desc": forms.Textarea(
                attrs={"placeholder": "Ingrese una descripción", "rows": 3, "cols": 3}
            ),
            "iva": forms.TextInput(),
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


class SucursalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["denominacion"].widget.attrs["autofocus"] = True
        for form in self.visible_fields():
            form.field.widget.attrs.update(
                {"class": "form-control", "autocomplete": "off"}
            )

    class Meta:
        model = Sucursal
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "denominacion": forms.TextInput(attrs={"placeholder": "Ingrese un nombre"}),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono convencional"}
            ),
            "direccion": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección"}
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


class PersonaForm(ModelForm):
    class NacionalidadModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.nacionalidad

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ci"].widget.attrs["autofocus"] = True
        # ESTADO CIVIL
        estado_civil = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="ESTADO_CIVIL"),
            # to_field_name="cod",
            empty_label="(Ninguno)",
            label="Estado Civil",
        )
        estado_civil.widget.attrs.update({"class": "form-control select2"})
        self.fields["estado_civil"] = estado_civil
        # GENERO
        sexo = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="SEXO"),
            # to_field_name="cod",
            empty_label="(Ninguno)",
            label="Género",
        )
        sexo.widget.attrs.update({"class": "form-control select2"})
        self.fields["sexo"] = sexo
        
        # NACIONALIDAD
        nacionalidad = self.NacionalidadModelChoiceField(
            queryset=Pais.objects.all(), empty_label="(Ninguno)"
        )
        nacionalidad.widget.attrs.update(
            {"class": "form-control select2", "style": "width: 100%;"}
        )
        self.fields["nacionalidad"] = nacionalidad
        self.fields["ciudad"].queryset = Ciudad.objects.none()
        if self.instance:
            self.fields["ciudad"].queryset = Ciudad.objects.filter(
                id=self.instance.ciudad_id
            )
        

    class Meta:
        model = Persona
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "ci": forms.TextInput(attrs={"placeholder": "Ingrese CI"}),
            "ruc": forms.TextInput(attrs={"placeholder": "Ingrese RUC"}),
            "nombre": forms.TextInput(attrs={"placeholder": "Ingrese nombre"}),
            "apellido": forms.TextInput(attrs={"placeholder": "Ingrese apellido"}),
            # 'nacionalidad': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            "ciudad": forms.Select(
                attrs={"class": "custom-select select2", "style": "width: 100%;"}
            ),
            "barrio": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "direccion": forms.TextInput(
                attrs={"placeholder": "Indique una dirección particular"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Indique un numero de telefono convencional"}
            ),
            "celular": forms.TextInput(
                attrs={"placeholder": "Indique un numero de telefono celular principal"}
            ),
            "email": forms.TextInput(attrs={"placeholder": "Indique un email principal"}),
            "fec_nacimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_nacimiento",
                    "value": get_fecha_actual_ymd,
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_nacimiento",
                },
            ),
            "nacionalidad": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            # 'estado_civil': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
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

