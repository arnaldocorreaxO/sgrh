from django.http import JsonResponse
from core.base.models import Barrio, Ciudad, RefDet
from django.db.models import Q

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

def ajax_ciudades(request):
    q = request.GET.get("q", "")
    
    # Usamos select_related para traer el distrito en la misma consulta
    # Ordenamos por distrito para facilitar la agrupación
    qs = Ciudad.objects.select_related('distrito').filter(
        Q(activo=True) & 
        (Q(distrito__denominacion__icontains=q) | Q(denominacion__icontains=q))
    ).order_by("distrito__denominacion", "denominacion")[:25]

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
        distritos_map[d_id]["children"].append({
            "id": i.id, 
            "text": str(i)
        })

    data = [{"id": "", "text": "------------"}] + results
    return JsonResponse(data, safe=False)

def ajax_barrios(request):
    # Consolidamos la obtención de IDs buscando en ambos diccionarios
    ciudad_ids = request.POST.getlist("id[]") or request.GET.getlist("id[]") or request.GET.getlist("id")
    
    data = [{"id": "", "text": "---------"}]
    
    if ciudad_ids:
        # select_related('ciudad') es vital para que toJSON() no haga más queries
        barrios = Barrio.objects.filter(ciudad_id__in=ciudad_ids).select_related('ciudad')
        
        for i in barrios:
            data.append({
                "id": i.id, 
                "text": str(i), 
                "data": i.ciudad.toJSON() 
            })
            
    return JsonResponse(data, safe=False)


# def ajax_ciudad(request):
#         q = request.GET.get("q", "")
#         qs = Ciudad.objects.filter(
#             Q(activo__exact=True)
#             & (
#                 Q(distrito__denominacion__icontains=q)
#                 | Q(denominacion__icontains=q)
#             )
#         ).order_by("denominacion", "distrito_id")[0:25]

#         data = [{"id": "", "text": "------------"}]
#         id_dpto_aux = 0
#         for i in qs:
#             if id_dpto_aux != i.distrito_id:
#                 data.append(
#                     {
#                         "text": str(i.distrito),
#                         "children": [{"id": i.id, "text": str(i)}],
#                     }
#                 )
#             else:
#                 data.append(
#                     {
#                         "children": [{"id": i.id, "text": str(i)}],
#                     }
#                 )
#             id_dpto_aux = i.distrito_id
#         return JsonResponse(data, safe=False)

# def ajax_barrios(request):
#     data = [{"id": "", "text": "---------"}]
#     ciudad_list = None
#     if "id" in request.GET:
#         ciudad_list = [request.POST["id"] if "id" in request.POST else None]

#     elif "id[]" in request.POST:
#         ciudad_list = (
#             request.POST.getlist("id[]") if "id[]" in request.POST else None
#         )
#     if ciudad_list:
#         for i in Barrio.objects.filter(ciudad_id__in=ciudad_list):
#             data.append(
#                 {"id": i.id, "text": str(i), "data": i.ciudad.toJSON()}
#             )
#     return JsonResponse(data,safe=False)