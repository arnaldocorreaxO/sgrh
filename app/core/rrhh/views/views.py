from django.http import JsonResponse
from core.rrhh.models import Institucion


def ajax_instituciones(request):
    term = request.GET.get("term", "")
    print("Term:", term)
    instituciones = Institucion.search(term)

    data = [{"id": institucion.id, "text": str(institucion)} for institucion in instituciones]

    return JsonResponse(data, safe=False)