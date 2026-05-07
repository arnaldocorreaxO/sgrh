from django.http import JsonResponse
from core.base.models import Barrio, Ciudad, RefDet
from django.db.models import Q

from django.http import JsonResponse
from django.db.models import Q


def ajax_empresas(request):
    # 1. Obtenemos el término y lo limpiamos
    q = request.GET.get("q", "").strip()

    # Iniciamos el QuerySet con el filtro base (siempre deben ser "EMPRESA")
    queryset = RefDet.objects.filter(refcab__cod_referencia="EMPRESA")

    # 2. Aplicamos la lógica de búsqueda por palabras si existe q
    if q:
        words = q.split()
        for word in words:
            # Encadenamos filtros: cada palabra debe estar en la denominación
            queryset = queryset.filter(denominacion__icontains=word)

    # 3. Ejecutamos la consulta con valores específicos y límite
    # Usamos .distinct() por seguridad al filtrar dinámicamente
    empresas = queryset.values("id", "denominacion").distinct()[:10]

    # 4. Formateamos para Select2 u otros componentes
    results = [{"id": e["id"], "text": e["denominacion"]} for e in empresas]

    return JsonResponse(results, safe=False)


def ajax_cargos(request):
    # 1. Obtenemos el término y limpiamos espacios sobrantes
    q = request.GET.get("q", "").strip()

    # 2. Filtro base obligatorio (solo registros tipo CARGO)
    queryset = RefDet.objects.filter(refcab__cod_referencia="CARGO")

    # 3. Aplicamos lógica multipalabra si hay un término de búsqueda
    if q:
        words = q.split()
        for word in words:
            # Filtramos acumulativamente: cada palabra debe existir en la denominación
            queryset = queryset.filter(denominacion__icontains=word)

    # 4. Seleccionamos campos, evitamos duplicados y limitamos a 10
    cargos = queryset.values("id", "denominacion").distinct()[:10]

    # 5. Formateamos la respuesta para el componente (Select2, etc.)
    results = [{"id": c["id"], "text": c["denominacion"]} for c in cargos]

    return JsonResponse(results, safe=False)


def ajax_ciudades(request):
    q = request.GET.get("q", "")

    # Usamos select_related para traer el distrito en la misma consulta
    # Ordenamos por distrito para facilitar la agrupación
    qs = (
        Ciudad.objects.select_related("distrito")
        .filter(
            Q(activo=True)
            & (Q(distrito__denominacion__icontains=q) | Q(denominacion__icontains=q))
        )
        .order_by("distrito__denominacion", "denominacion")[:25]
    )

    results = []
    distritos_map = {}

    for i in qs:
        d_id = i.distrito_id
        d_nom = str(i.distrito)

        if d_id not in distritos_map:
            # Creamos el grupo del distrito
            distrito_entry = {"text": d_nom, "children": []}
            distritos_map[d_id] = distrito_entry
            results.append(distrito_entry)

        # Añadimos la ciudad al grupo correspondiente
        distritos_map[d_id]["children"].append({"id": i.id, "text": str(i)})

    data = [{"id": "", "text": "------------"}] + results
    return JsonResponse(data, safe=False)


def ajax_barrios(request):
    # Consolidamos la obtención de IDs buscando en ambos diccionarios
    ciudad_ids = (
        request.POST.getlist("id[]")
        or request.GET.getlist("id[]")
        or request.GET.getlist("id")
    )

    data = [{"id": "", "text": "---------"}]

    if ciudad_ids:
        # select_related('ciudad') es vital para que toJSON() no haga más queries
        barrios = Barrio.objects.filter(ciudad_id__in=ciudad_ids).select_related(
            "ciudad"
        )

        for i in barrios:
            data.append({"id": i.id, "text": str(i), "data": i.ciudad.toJSON()})

    return JsonResponse(data, safe=False)
