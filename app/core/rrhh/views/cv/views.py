
from django.views.generic import DetailView, View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from core.rrhh.models import Empleado

class CVEmpleadoView(DetailView):
    model = Empleado
    template_name = 'empleado/cv_empleado.html'
    context_object_name = 'empleado'

class CVEmpleadoPDFView(View):
    def get(self, request, pk):
        empleado = get_object_or_404(Empleado, pk=pk)
        html_string = render_to_string('cv_empleado.html', {'empleado': empleado})
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="cv_{empleado.nombre}.pdf"'
        return response

