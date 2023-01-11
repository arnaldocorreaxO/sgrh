
from core.bascula.models import  Chofer, Cliente,  Producto, Transporte, Vehiculo
from django import forms

from core.base.models import Sucursal

class ReportForm(forms.Form):
    # Extra Fields
    date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))
    time_range_in = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))
    time_range_out = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))
    
    SITUACION=(
		('PEND','PENDIENTES'),
		('RECI','RECIBIDOS'),
		
	)	
    choiceSituacion = SITUACION + (('', '(Todos)'),)

    # cliente = forms.ModelChoiceField(queryset=Cliente.objects.filter(activo__exact=True).order_by('denominacion'), empty_label="(Todos)")
    # producto = forms.ModelChoiceField(queryset=Producto.objects.filter(activo__exact=True).order_by('denominacion'), empty_label="(Todos)")
    # vehiculo = forms.ModelChoiceField(queryset=Vehiculo.objects.filter(activo__exact=True).order_by('matricula'), empty_label="(Todos)")
    # chofer = forms.ModelChoiceField(queryset=Chofer.objects.filter(activo__exact=True).order_by('nombre','apellido'), empty_label="(Todos)")
    sucursal = forms.ModelChoiceField(queryset=Sucursal.objects.filter(activo=True), empty_label="(Todos)")
    transporte = forms.ModelChoiceField(queryset=Transporte.objects.filter(activo=True), empty_label="(Todos)")
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.none(), empty_label="(Todos)")
    destino = forms.ModelChoiceField(queryset=Cliente.objects.filter(activo=True,ver_en_destino=True), empty_label="(Todos)")
    producto = forms.ModelChoiceField(queryset=Producto.objects.none(), empty_label="(Todos)")
    vehiculo = forms.ModelChoiceField(queryset=Vehiculo.objects.none(), empty_label="(Todos)")
    chofer = forms.ModelChoiceField(queryset=Chofer.objects.none(), empty_label="(Todos)")
    situacion = forms.ChoiceField(choices=choiceSituacion)
   
    sucursal.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    transporte.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    cliente.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    destino.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    producto.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    vehiculo.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    chofer.widget.attrs.update({'class': 'form-control select2','multiple':'true'})    
    situacion.widget.attrs.update({'class': 'form-control select2'})    