from django.http import JsonResponse
from core.base.models import RefDet

def ajax_empresas(request):
    q = request.GET.get("q", "")

    # Filtramos por denominación y limitamos a los primeros 10 resultados
    empresas = RefDet.objects.filter(
        refcab__cod_referencia="EMPRESA",
        denominacion__icontains=q
    ).values("id", "denominacion")[:10]

    results = [
        {"id": e["id"], "text": e["denominacion"]}
        for e in empresas
    ]

    return JsonResponse(results, safe=False)

def ajax_cargos(request):
    q = request.GET.get("q", "")

    # Filtramos por denominación y limitamos a los primeros 10
    cargos = RefDet.objects.filter(
        refcab__cod_referencia="CARGO",
        denominacion__icontains=q
    ).values("id", "denominacion")[:10] # El [:10] aplica el LIMIT 10 en SQL

    results = [
        {"id": c["id"], "text": c["denominacion"]}
        for c in cargos
    ]

    return JsonResponse(results, safe=False)