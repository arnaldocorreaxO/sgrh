from django import forms
from django.forms import ModelForm
from core.base.models import RefDet
from core.rrhh.empleado.forms import ModelFormEmpleado
from core.rrhh.models import CategoriaSalarial, Dependencia, DependenciaPosicion, EmpleadoPosicion

# FORMULARIO FILTRO EMPLEADO
class EmpleadoPosicionFilterForm(forms.Form):

    dependencia_padre = forms.ModelChoiceField(
        queryset=Dependencia.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            "label": "Dependencia Superior",
            "class": "form-control select2",
            "placeholder": "Seleccione Dependencia Superior...",
            "style": "width: 100%;",
            "id": "id_dependencia_padre",
        })
    )   

    dependencia_hija = forms.ModelChoiceField(
        queryset=Dependencia.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            "label": "Dependencia Inferior",
            "class": "form-control select2",
            "placeholder": "Seleccione Dependencia Inferior...",
            "style": "width: 100%;",
            "id": "id_dependencia_hija",
        })
    )   

    tipo_movimiento = forms.ModelChoiceField(
        queryset=RefDet.objects.filter(refcab__cod_referencia="TIPO_MOVIMIENTO_EMPLEADO_POSICION").order_by('denominacion'),
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "placeholder": "Seleccione Tipo de Movimiento...",
            "style": "width: 100%;",
            "id": "id_tipo_movimiento",
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

class EmpleadoPosicionForm(ModelFormEmpleado):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

        self.fields["tipo_movimiento"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="TIPO_MOVIMIENTO_EMPLEADO_POSICION"
        ).order_by('denominacion')

        self.fields["categoria_salarial"].queryset = CategoriaSalarial.objects.all().order_by('denominacion')

        
        self.fields["vinculo_laboral"].queryset = RefDet.objects.filter(
            refcab__cod_referencia="VINCULO_LABORAL"
        ).order_by('denominacion')
        
        # Estilo específico para el checkbox
        self.fields['cargo_puesto_actual'].widget.attrs.update({
                'class': 'form-check-input ml-2', # 'ml-2' añade margen a la izquierda si el label va antes
                'style': 'cursor: pointer; margin-right: 10px;' # Esto es infalible
            })

        # --- LÓGICA PARA CAMPO DEPENDENCIA_POSICION (Rehidratación para AJAX) ---
        if 'dependencia_posicion' in self.data:
            try:
                dependencia_posicion_id = int(self.data.get('dependencia_posicion'))
                self.fields["dependencia_posicion"].queryset = DependenciaPosicion.objects.filter(id=dependencia_posicion_id)
            except (ValueError, TypeError):
                self.fields["dependencia_posicion"].queryset = DependenciaPosicion.objects.none()
        elif self.instance and self.instance.dependencia_posicion_id:
            self.fields["dependencia_posicion"].queryset = DependenciaPosicion.objects.filter(id=self.instance.dependencia_posicion_id)
        else:
            self.fields["dependencia_posicion"].queryset = DependenciaPosicion.objects.none()

        self.fields["dependencia_posicion"].widget.attrs.update({
                "class": "form-control select2",
                "style": "width: 100%;"
            })
        self.fields["categoria_salarial"].widget.attrs.update({
                "class": "form-control select2",
                "style": "width: 100%;"
            })

    class Meta:
        model = EmpleadoPosicion
        fields = [
            'empleado', 'legajo', 'dependencia_posicion', 'categoria_salarial',
            'tipo_movimiento', 'vinculo_laboral', 'fecha_inicio', 
            'fecha_fin', 'cargo_puesto_actual', 'archivo_pdf'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'legajo': forms.TextInput(attrs={'placeholder': 'Indique el legajo del empleado'}),
        }