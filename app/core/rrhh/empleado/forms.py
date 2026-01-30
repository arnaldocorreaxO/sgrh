from django import forms
from django.forms import ModelForm, ValidationError
from core.base.models import Sucursal
from core.base.utils import get_fecha_actual_ymd
from core.base.forms import readonly_fields
from core.rrhh.models import Empleado, RefDet, Pais, Ciudad
from django.forms.widgets import ClearableFileInput

# FORMULARIO FILTRO EMPLEADO
class EmpleadoFilterForm(forms.Form):
    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.none(), # Por defecto vacío
        empty_label="(Seleccione una Sucursal)",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "style": "width: 100%;",
            "id": "sucursal_id",
        })
    )
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.none(), # Por defecto vacío
        empty_label="(Seleccione un empleado)",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "style": "width: 100%;",
            "id": "empleado_id",
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # 1. Determinar nivel de acceso
            es_global = user.is_superuser or user.groups.filter(name='ADMIN_RRHH_GLOBAL').exists()
            
            # 2. Lógica para el campo SUCURSAL
            if es_global:
                # Ve todas las sucursales
                sucursales_qs = Sucursal.objects.all()
            else:
                # Ve solo su sucursal (basado en el campo sucursal de tu modelo User)
                sucursales_qs = Sucursal.objects.filter(id=user.sucursal_id)
            
            self.fields['sucursal'].queryset = sucursales_qs.order_by('denominacion')
            
            # Predeterminar la sucursal del usuario
            if user.sucursal_id:
                self.fields['sucursal'].initial = user.sucursal_id
                
                # Opcional: Si NO es global, puedes bloquear el campo para que no lo cambie
                if not es_global:
                    self.fields['sucursal'].widget.attrs['disabled'] = True # O usar disabled
            
            # 3. Lógica para el campo EMPLEADO (reutilizando tu lógica)
            emp_qs = Empleado.objects.filter(activo=True)
            
            if not es_global:
                # Filtrar empleados por la sucursal del usuario
                emp_qs = emp_qs.filter(sucursal_id=user.sucursal_id)
            
            self.fields['empleado'].queryset = emp_qs.order_by('nombre', 'apellido')

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
            self.fields["empleado"].queryset = Empleado.objects.none()
            if self.instance and self.instance.empleado_id:
                self.fields["empleado"].queryset = Empleado.objects.filter(id=self.instance.empleado_id)
            
            self.fields["empleado"].widget.attrs.update({
                "class": "form-control select2",
                "style": "width: 100%;"
            })


# FORMULARIO EMPLEADO
class EmpleadoForm(forms.ModelForm):
    # --- Campos definidos a nivel de clase para correcta validación ---
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'autocomplete': 'off'
        }),
        label='Imagen',
        required=False
    )

    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.all(),
        empty_label="(Ninguno)",
        label="Sucursal",
        widget=forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"})
    )

    estado_civil = forms.ModelChoiceField(
        queryset=RefDet.objects.filter(refcab__cod_referencia="ESTADO_CIVIL"),
        empty_label="(Ninguno)",
        label="Estado Civil",
        widget=forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"})
    )

    sexo = forms.ModelChoiceField(
        queryset=RefDet.objects.filter(refcab__cod_referencia="SEXO"),
        empty_label="(No especificado)",
        label="Género",
        widget=forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"})
    )

    tipo_sanguineo = forms.ModelChoiceField(
        queryset=RefDet.objects.filter(refcab__cod_referencia="TIPO_SANGUINEO"),
        empty_label="(No especificado)",
        label="Tipo Sanguíneo",
        widget=forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"})
    )

    # Clase interna personalizada para el campo Nacionalidad
    class NacionalidadModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.nacionalidad

    nacionalidad = NacionalidadModelChoiceField(
        queryset=Pais.objects.all(),
        empty_label="(No especificado)",
        label="Nacionalidad",
        widget=forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"})
    )

    class Meta:
        model = Empleado
        fields = "__all__"
        # exclude = readonly_fields  # Asegúrate de que readonly_fields esté definido antes
        widgets = {
            "legajo": forms.TextInput(attrs={"placeholder": "Legajo actual del empleado"}),
            "ci": forms.TextInput(attrs={"placeholder": "Ingrese CI"}),
            "ruc": forms.TextInput(attrs={"placeholder": "Ingrese RUC"}),
            "nombre": forms.TextInput(attrs={"placeholder": "Ingrese nombre"}),
            "apellido": forms.TextInput(attrs={"placeholder": "Ingrese apellido"}),
            "sucursal": forms.Select(attrs={"class": "custom-select select2", "style": "width: 100%;"}),
            "tipo_sanguineo": forms.Select(attrs={"class": "custom-select select2", "style": "width: 100%;"}),
            "ciudad": forms.Select(attrs={"class": "custom-select select2", "style": "width: 100%;"}),
            "barrio": forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"}),
            "direccion": forms.TextInput(attrs={"placeholder": "Indique una dirección particular"}),
            "telefono": forms.TextInput(attrs={"placeholder": "Indique un número de teléfono convencional"}),
            "celular": forms.TextInput(attrs={"placeholder": "Indique un número de celular principal"}),
            "email": forms.TextInput(attrs={"placeholder": "Indique un email principal"}),
            "ci_fecha_vencimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "ci_fecha_vencimiento",
                    "data-toggle": "datetimepicker",
                    "data-target": "#ci_fecha_vencimiento",
                },
            ),
            "fecha_nacimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fecha_nacimiento",
                    "data-toggle": "datetimepicker",
                    "data-target": "#fecha_nacimiento",
                },
            ),
            'ci_archivo_pdf': ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Atributos de estado y visualización
        self.fields["legajo"].disabled = True
        self.fields["ci"].widget.attrs["autofocus"] = True

        # 2. Cargar imagen inicial desde el usuario relacionado
        if self.instance.pk and hasattr(self.instance, 'usuario') and self.instance.usuario.image:
            self.initial['image'] = self.instance.usuario.image

        # 3. Lógica dinámica de Ciudad (Filtrado inicial)
        self.fields["ciudad"].queryset = Ciudad.objects.none()
        
        if 'ciudad' in self.data: # Datos provenientes del POST
            try:
                ciudad_id = int(self.data.get('ciudad'))
                self.fields['ciudad'].queryset = Ciudad.objects.filter(id=ciudad_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.ciudad: # Datos del objeto existente
            self.fields["ciudad"].queryset = Ciudad.objects.filter(id=self.instance.ciudad_id)

    # --- Validaciones ---
    def clean_ci(self):
        ci = self.cleaned_data.get("ci")
        if ci:
            queryset = Empleado.objects.filter(ci__iexact=ci)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("Ya existe Empleado con este CI.")
        return ci

    def clean_ruc(self):
        ruc = self.cleaned_data.get("ruc")
        if ruc:
            queryset = Empleado.objects.filter(ruc__iexact=ruc)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("Ya existe Empleado con este RUC.")
        return ruc
    
    # ---------------------------------------------------------
    # VALIDACIÓN CI ARCHIVO PDF
    # ---------------------------------------------------------
    def clean_ci_archivo_pdf(self):
        archivo = self.cleaned_data.get('ci_archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise ValidationError('El archivo debe ser un PDF.')
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no debe exceder 5MB.')
        return archivo

def save(self, commit=True):
    # 1. No llames a is_valid() aquí; el save asume que los datos ya están limpios.
    # Usamos el save del padre para obtener la instancia del empleado
    empleado = super().save(commit=False)
    
    try:
        # --- Manejo del Usuario Relacionado (Imagen) ---
        # Usamos getattr por seguridad si la relación es opcional
        usuario = getattr(empleado, 'usuario', None)
        
        if usuario:
            image_data = self.cleaned_data.get("image")
            
            # Caso: Checkbox de borrar imagen marcado (False)
            if image_data is False:
                if usuario.image:
                    usuario.image.delete(save=False)
                usuario.image = None
            # Caso: Nueva imagen cargada
            elif image_data:
                usuario.image = image_data
            
            usuario.save()

        # --- Manejo del PDF (Archivo en el mismo modelo Empleado) ---
        archivo_pdf_data = self.cleaned_data.get('archivo_pdf')
        
        if archivo_pdf_data is False:  # Se marcó "Limpiar" en el widget del PDF
            if empleado.archivo_pdf:
                empleado.archivo_pdf.delete(save=False)
            empleado.archivo_pdf = None
        # Si hay un archivo nuevo, super().save(commit=False) ya lo asignó a 'empleado'

        if commit:
            empleado.save()
            
    except Exception as e:
        # Si usas esto en una vista AJAX, asegúrate de que 'data' sea accesible
        # o maneja el error según tu lógica de negocio.
        raise e 
        
    return empleado  # 🔑 devolver la instancia, no un dict
    
# # FORMULARIO EMPLEADO
# class EmpleadoForm(ModelFormEmpleado):
#     image = forms.ImageField(
#         widget=ClearableFileInput(attrs={
#             'class': 'form-control-file',
#             'autocomplete': 'off'
#         }),
#         label='Imagen',
#         required=False
#     )

#     class NacionalidadModelChoiceField(forms.ModelChoiceField):
#         def label_from_instance(self, obj):
#             return obj.nacionalidad

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Hacer legajo de solo lectura
#         self.fields["legajo"].disabled = True
#         # Autofocus en CI
#         self.fields["ci"].widget.attrs["autofocus"] = True
#         # Imagen inicial si existe
#         if self.instance and self.instance.usuario and self.instance.usuario.image:
#             self.initial['image'] = self.instance.usuario.image


#         # Estado civil
#         estado_civil = forms.ModelChoiceField(
#             queryset=RefDet.objects.filter(refcab__cod_referencia="ESTADO_CIVIL"),
#             empty_label="(Ninguno)",
#             label="Estado Civil"
#         )
#         estado_civil.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
#         self.fields["estado_civil"] = estado_civil

#         # Género
#         sexo = forms.ModelChoiceField(
#             queryset=RefDet.objects.filter(refcab__cod_referencia="SEXO"),
#             empty_label="(Ninguno)"
#         )
#         sexo.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
#         self.fields["sexo"] = sexo

#         # Nacionalidad
#         nacionalidad = self.NacionalidadModelChoiceField(
#             queryset=Pais.objects.all(), empty_label="(Ninguno)"
#         )
#         nacionalidad.widget.attrs.update({"class": "form-control select2", "style": "width: 100%;"})
#         self.fields["nacionalidad"] = nacionalidad

#         # Ciudad dinámica
#         self.fields["ciudad"].queryset = Ciudad.objects.none()
#         if self.instance and self.instance.ciudad_id:
#             self.fields["ciudad"].queryset = Ciudad.objects.filter(id=self.instance.ciudad_id)
        

#     class Meta:
#         model = Empleado
#         fields = "__all__"
#         exclude = readonly_fields
#         widgets = {
#             "legajo": forms.TextInput(attrs={"placeholder": "Legajo actual del empleado"}),
#             "ci": forms.TextInput(attrs={"placeholder": "Ingrese CI"}),
#             "ruc": forms.TextInput(attrs={"placeholder": "Ingrese RUC"}),
#             "nombre": forms.TextInput(attrs={"placeholder": "Ingrese nombre"}),
#             "apellido": forms.TextInput(attrs={"placeholder": "Ingrese apellido"}),
#             "ciudad": forms.Select(attrs={"class": "custom-select select2", "style": "width: 100%;"}),
#             "barrio": forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"}),
#             "direccion": forms.TextInput(attrs={"placeholder": "Indique una dirección particular"}),
#             "telefono": forms.TextInput(attrs={"placeholder": "Indique un número de teléfono convencional"}),
#             "celular": forms.TextInput(attrs={"placeholder": "Indique un número de celular principal"}),
#             "email": forms.TextInput(attrs={"placeholder": "Indique un email principal"}),
#             "fec_nacimiento": forms.DateInput(
#                 format="%Y-%m-%d",
#                 attrs={
#                     "class": "form-control datetimepicker-input",
#                     "id": "fec_nacimiento",
#                     "value": get_fecha_actual_ymd,
#                     "data-toggle": "datetimepicker",
#                     "data-target": "#fec_nacimiento",
#                 },
#             ),
#             "nacionalidad": forms.Select(attrs={"class": "form-control select2", "style": "width: 100%;"}),
#         }

#     # Validación de CI
#     def clean_ci(self):
#         ci = self.cleaned_data.get("ci")
#         if ci and Empleado.objects.filter(ci__iexact=ci).exclude(pk=self.instance.pk).exists():
#             raise ValidationError("Ya existe Empleado con este CI.")
#         return ci

#     # Validación de RUC
#     def clean_ruc(self):
#         ruc = self.cleaned_data.get("ruc")
#         if ruc and Empleado.objects.filter(ruc__iexact=ruc).exclude(pk=self.instance.pk).exists():
#             raise ValidationError("Ya existe Empleado con este RUC.")
#         return ruc


#     def save(self, commit=True):
#         empleado = super().save(commit=False)
#         usuario = empleado.usuario

#         # Manejo de imagen
#         if self.cleaned_data.get("image") is False:  # Checkbox de limpieza marcado
#             if usuario.image:
#                 usuario.image.delete(save=False)
#             usuario.image = None
#         elif self.cleaned_data.get("image"):
#             usuario.image = self.cleaned_data["image"]

#         usuario.save()
#         if commit:
#             empleado.save()
#         return empleado  # 🔑 devolver la instancia, no un dict





