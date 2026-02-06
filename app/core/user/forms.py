from crum import get_current_request

from django.contrib.auth import update_session_auth_hash
from django.forms import ModelForm

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User


class UserForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["groups"].required = True
		self.fields["first_name"].widget.attrs["autofocus"] = True

	class Meta:
		model = User
		fields = (
			"first_name",
			"last_name",
			"username",
			"password",
			"dni",
			"email",
			"groups",
			"image",
			"sucursal",
			"is_active",
			"is_staff",
			"is_superuser",
			"is_change_password",
			
		)
		
		widgets = {
			"first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese sus nombres"}),
			"last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese sus apellidos"}),
			"username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese un nombre de usuario"}),
			"dni": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese su número de cédula"}),
			"email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Ingrese su correo electrónico"}),
			"password": forms.PasswordInput(
				render_value=True, 
				attrs={"class": "form-control", "placeholder": "Ingrese una contraseña"}
			),
			"sucursal": forms.Select(attrs={"class": "form-control select2", "style": "width:100%"}),
			"caja": forms.Select(attrs={"class": "form-control select2", "style": "width:100%"}),
			"groups": forms.SelectMultiple(
				attrs={
					"class": "form-control select2",
					"multiple": "multiple",
					"style": "width:100%",
				}
			),
			"is_change_password": forms.CheckboxInput(attrs={
				"class": "form-check-input",
				"style": "position: relative; margin-left: 0; margin-right: 10px; cursor: pointer; transform: scale(1.3);"
			}),
		}
		labels = {
				'is_change_password': 'Cambiar contraseña en el próximo inicio de sesión',
			}
		exclude = [
				# "is_change_password",
				"user_permissions",
				"date_joined",
				"last_login",
				"token",
			]

	def update_session(self, user):
		request = get_current_request()
		if user == request.user:
			update_session_auth_hash(request, user)

	def save(self, commit=True):
		data = {}
		form = super()
		try:
			if form.is_valid():
				pwd = self.cleaned_data["password"]
				u = form.save(commit=False)
				if u.pk is None:
					u.set_password(pwd)
				else:
					user = User.objects.get(pk=u.pk)
					if user.password != pwd:
						u.set_password(pwd)
				u.save()

				u.groups.clear()
				for g in self.cleaned_data["groups"]:
					u.groups.add(g)

				self.update_session(u)
			else:
				data["error"] = form.errors
		except Exception as e:
			data["error"] = str(e)
		return data


class ProfileForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["first_name"].widget.attrs["autofocus"] = True

	class Meta:
		model = User
		fields = "first_name", "last_name", "username", "dni", "email", "image"
		widgets = {
			"first_name": forms.TextInput(attrs={"placeholder": "Ingrese sus nombres"}),
			"last_name": forms.TextInput(
				attrs={"placeholder": "Ingrese sus apellidos"}
			),
			"username": forms.TextInput(
				attrs={"placeholder": "Ingrese un nombre de usuario"}
			),
			"dni": forms.TextInput(
				attrs={"placeholder": "Ingrese su número de cedula"}
			),
			"email": forms.TextInput(
				attrs={"placeholder": "Ingrese su correo electrónico"}
			),
		}
		exclude = [
			"is_change_password",
			"is_active",
			"is_staff",
			"user_permissions",
			"password",
			"date_joined",
			"last_login",
			"is_superuser",
			"groups",
			"token",
		]

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

# Formulario para forzar el cambio de contraseña
class ForcePasswordChangeForm(PasswordChangeForm):
	def clean_new_password1(self):
		new_password = self.cleaned_data.get("new_password1")
		# Validamos contra el hash actual del Custom User
		if self.user.check_password(new_password):
			raise ValidationError(
				"La nueva contraseña no puede ser igual a la actual. Por favor, elija una diferente."
			)
		return new_password