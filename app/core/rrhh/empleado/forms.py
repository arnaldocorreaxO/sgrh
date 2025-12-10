from django import forms
from django.forms import ModelForm, ValidationError
from core.base.utils import get_fecha_actual_ymd
from core.base.forms import readonly_fields
from core.rrhh.models import Empleado, RefDet, Pais, Ciudad
from django.forms.widgets import ClearableFileInput

# FORMULARIO FILTRO EMPLEADO
class EmpleadoFilterForm(forms.Form):
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).order_by('nombre', 'apellido'),
        empty_label="(Seleccione un empleado)",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "style": "width: 100%;",
            "id": "empleado",
        })
    )

# BASE PARA FORMULARIOS CON CAMPO EMPLEADO
class ModelFormEmpleado(ModelForm):
    """
    Base para formularios que incluyen el campo 'empleado'.
    - Si es self_view: oculta el campo y se asigna automáticamente en la vista.
    - Si es admin: muestra el campo como un select para elegir empleado.
    """

    def __init__(self, *args, **kwargs):
        # Flag que viene desde la vista (EmpleadoScopedMixin lo pasa)
        is_self_view = kwargs.pop("is_self_view", False)
        super().__init__(*args, **kwargs)

        if is_self_view:
            # Ocultar campo empleado en modo self
            self.fields.pop("empleado", None)
        else:
            # Mostrar campo empleado en modo admin
            empleado_field = forms.ModelChoiceField(
                queryset=Empleado.objects.all(),
                empty_label="(Seleccione un empleado)",
                label="Empleado",
            )
            empleado_field.widget.attrs.update({
                "class": "form-control select2",
                "style": "width: 100%;"
            })
            self.fields["empleado"] = empleado_field


# FORMULARIO EMPLEADO
class EmpleadoForm(ModelFormEmpleado):
    image = forms.ImageField(
        widget=ClearableFileInput(attrs={
            'class': 'form-control-file',
            'autocomplete': 'off'
        }),
        label='Imagen',
        required=False
    )

    class NacionalidadModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.nacionalidad

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer legajo de solo lectura
        self.fields["legajo"].disabled = True
        # Autofocus en CI
        self.fields["ci"].widget.attrs["autofocus"] = True
        # Imagen inicial si existe
        if self.instance and self.instance.usuario and self.instance.usuario.image:
            self.initial['image'] = self.instance.usuario.image


        # Estado civil
        estado_civil = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia="ESTADO_CIVIL"),
            empty_label="(Ninguno)",
            label="Estado Civil"
        )
        estado_civil.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["estado_civil"] = estado_civil

        # Género
        sexo = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia="SEXO"),
            empty_label="(Ninguno)"
        )
        sexo.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["sexo"] = sexo

        # Nacionalidad
        nacionalidad = self.NacionalidadModelChoiceField(
            queryset=Pais.objects.all(), empty_label="(Ninguno)"
        )
        nacionalidad.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
        self.fields["nacionalidad"] = nacionalidad

        # Ciudad dinámica
        self.fields["ciudad"].queryset = Ciudad.objects.none()
        if self.instance and self.instance.ciudad_id:
            self.fields["ciudad"].queryset = Ciudad.objects.filter(id=self.instance.ciudad_id)

    class Meta:
        model = Empleado
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "legajo": forms.TextInput(attrs={"placeholder": "Legajo actual del empleado"}),
            "ci": forms.TextInput(attrs={"placeholder": "Ingrese CI"}),
            "ruc": forms.TextInput(attrs={"placeholder": "Ingrese RUC"}),
            "nombre": forms.TextInput(attrs={"placeholder": "Ingrese nombre"}),
            "apellido": forms.TextInput(attrs={"placeholder": "Ingrese apellido"}),
            "ciudad": forms.Select(attrs={"class": "custom-select select2", "style": "width: 100%;"}),
            "barrio": forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"}),
            "direccion": forms.TextInput(attrs={"placeholder": "Indique una dirección particular"}),
            "telefono": forms.TextInput(attrs={"placeholder": "Indique un número de teléfono convencional"}),
            "celular": forms.TextInput(attrs={"placeholder": "Indique un número de celular principal"}),
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
            "nacionalidad": forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"}),
        }

    # Validación de CI
    def clean_ci(self):
        ci = self.cleaned_data.get("ci")
        if ci and Empleado.objects.filter(ci__iexact=ci).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Ya existe Empleado con este CI.")
        return ci

    # Validación de RUC
    def clean_ruc(self):
        ruc = self.cleaned_data.get("ruc")
        if ruc and Empleado.objects.filter(ruc__iexact=ruc).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Ya existe Empleado con este RUC.")
        return ruc


    def save(self, commit=True):
        empleado = super().save(commit=False)
        usuario = empleado.usuario

        # Manejo de imagen
        if self.cleaned_data.get("image") is False:  # Checkbox de limpieza marcado
            if usuario.image:
                usuario.image.delete(save=False)
            usuario.image = None
        elif self.cleaned_data.get("image"):
            usuario.image = self.cleaned_data["image"]

        usuario.save()
        if commit:
            empleado.save()
        return empleado  # 🔑 devolver la instancia, no un dict





