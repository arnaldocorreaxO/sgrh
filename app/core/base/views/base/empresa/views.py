import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from core.base.forms import Empresa, EmpresaForm
from core.security.mixins import ModuleMixin

class EmpresaUpdate( ModuleMixin,UpdateView):
    template_name = 'empresa/create.html'
    form_class = EmpresaForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        empresa = Empresa.objects.all()
        if empresa.exists():
            return empresa[0]
        return Empresa()

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            empresa = self.get_object()
            empresa.denominacion = request.POST['denominacion']
            empresa.ruc = request.POST['ruc']
            empresa.celular = request.POST['celular']
            empresa.telefono = request.POST['telefono']
            empresa.email = request.POST['email']
            empresa.website = request.POST['website']
            empresa.direccion = request.POST['direccion']
            if 'imagen' in request.FILES:
                empresa.imagen = request.FILES['imagen']
            if 'imagen-clear' in request.POST:
                empresa.remove_image()
            empresa.desc = request.POST['desc']
            empresa.iva = float(request.POST['iva'])
            empresa.save()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Configuración de la Empresa'
        return context
