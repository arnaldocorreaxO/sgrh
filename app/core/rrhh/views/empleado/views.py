import json
import json as simplejson
import math
from datetime import datetime


from django.contrib.auth.models import Group
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from config import settings
from core.rrhh.models import Empleado
from core.rrhh.forms.empleado.forms import EmpleadoForm
from core.base.models import Barrio, Ciudad
from core.base.procedures import sp_identificaciones
from core.base.utils import YYYY_MM_DD, get_fecha_actual, isNULL
from core.security.mixins import PermissionMixin
from core.user.models import User

# MSSQL
def get_datos_persona(request):
    # import pdb; pdb.set_trace()
    data = str(request.GET.get("ci", "X"))
    # print("*" * 10)
    # print(vCi)
    persona = sp_identificaciones(ci=data)
    # print(persona)
    return HttpResponse(simplejson.dumps(persona), content_type="application/json")

class EmpleadoUsuarioMixin:
    """
    Mixin institucional para obtener el empleado vinculado al usuario logueado
    y generar títulos personalizados para vistas.
    """

    def get_empleado_usuario(self):
        try:
            return Empleado.objects.get(usuario=self.request.user)
        except Empleado.DoesNotExist:
            return None

    def get_titulo_formacion(self, prefijo="Formación Académica"):
        empleado = self.get_empleado_usuario()
        if empleado:
            return f"{prefijo} de {empleado.nombre} {empleado.apellido}"
        return prefijo

    def enrich_context_with_empleado(self, context, prefijo="Formación Académica"):
        """
        Agrega 'title' y 'empleado' al contexto, reutilizable en ListView, CreateView, UpdateView.
        """
        empleado = self.get_empleado_usuario()
        context["title"] = f"{prefijo} de {empleado.nombre} {empleado.apellido}" if empleado else prefijo
        context["empleado"] = empleado
        return context


class EmpleadoList(ListView):
    model = Empleado
    template_name = "empleado/list.html"
    permission_required = "view_empleado"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        # print(request.POST)
        action = request.POST["action"]

        try:
            if action == "search":
                data = []

                _start = request.POST["start"]
                _length = request.POST["length"]
                _search = request.POST["search[value]"]

                _order = []

                for i in range(9):
                    _column_order = f"order[{i}][column]"
                    # print('Column Order:',_column_order)
                    if _column_order in request.POST:
                        _column_number = request.POST[_column_order]
                        _order.append(
                            request.POST[f"columns[{_column_number}][data]"].split(".")[
                                0
                            ]
                        )
                    if f"order[{i}][dir]" in request.POST:
                        _dir = request.POST[f"order[{i}][dir]"]
                        if _dir == "desc":
                            _order[i] = f"-{_order[i]}"

                _where = "1 = 1"
                qs = Empleado.objects.filter().extra(where=[_where]).order_by(*_order)
                if len(_search):
                    if _search.isnumeric():
                        qs.filter(Q(id__exact=_search) | Q(ci__exact=_search))
                    else:
                        qs = (
                            qs.filter(
                                Q(nombre__icontains=_search)
                                | Q(apellido__icontains=_search)
                            )
                            .exclude(activo=False)
                            .order_by("id")
                        )

                print(_where)

                total = qs.count()
                print(total)

                if _start and _length:
                    start = int(_start)
                    length = int(_length)
                    page = math.ceil(start / length) + 1
                    per_page = length

                if _length == "-1":
                    qs = qs[start:]
                else:
                    qs = qs[start : start + length]

                position = start + 1
                for i in qs:
                    item = i.toJSON()
                    # item['position'] = position
                    data.append(item)
                    position += 1

                data = {
                    "data": data,
                    "page": page,  # [opcional]
                    "per_page": per_page,  # [opcional]
                    "recordsTotal": total,
                    "recordsFiltered": total,
                }
            else:
                data["error"] = "No ha ingresado una opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("empleado_create")
        context["title"] = "Listado de Empleados"
        return context


# class EmpleadoCreate(PermissionMixin,CreateView):
class EmpleadoCreate(CreateView):
    model = Empleado
    template_name = "empleado/create.html"
    form_class = EmpleadoForm
    success_url = reverse_lazy("empleado_list")
    permission_required = "add_empleado"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        type = self.request.POST["type"]
        obj = self.request.POST["obj"].strip()
        print(type)
        print(obj)

        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            if type == "ci":
                if Empleado.objects.filter(ci__iexact=obj):
                    data["valid"] = False
            if type == "ruc":
                if Empleado.objects.filter(ruc__iexact=obj):
                    data["valid"] = False
            if type == "fec_nacimiento":
                fec_nacimiento = datetime.strptime(
                    obj, "%d/%m/%Y"
                )  # Este del from datetime
                edad = relativedelta(get_fecha_actual, fec_nacimiento)
                if edad.years:
                    if abs(edad.years) < 18:
                        data["valid"] = False
                else:
                    data["valid"] = False
        except Exception as e:
            print(str(e))
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "add":
                with transaction.atomic():
                    # Buscar usuario por DNI
                    usuario = User.objects.filter(dni=request.POST['ci']).first()

                    if usuario:
                        # 🔄 Actualizar datos existentes
                        usuario.first_name = request.POST['nombre']
                        usuario.last_name = request.POST['apellido']
                        usuario.email = request.POST['email']
                        usuario.sucursal_id = 1
                        if 'image' in request.FILES:
                            usuario.image = request.FILES['image']
                        usuario.create_or_update_password(request.POST['ci'])  # si aplica
                        usuario.save()
                        print(f"✅ Usuario actualizado: DNI {usuario.dni}")
                    else:
                        # 🆕 Crear nuevo usuario
                        usuario = User()
                        usuario.dni = request.POST['ci']
                        usuario.username = usuario.dni
                        usuario.first_name = request.POST['nombre']
                        usuario.last_name = request.POST['apellido']
                        usuario.email = request.POST['email']
                        usuario.sucursal_id = 1
                        if 'image' in request.FILES:
                            usuario.image = request.FILES['image']
                        usuario.create_or_update_password(usuario.dni)
                        usuario.save()
                        print(f"✅ Usuario creado: DNI {usuario.dni}")

                    # Asignar grupo
                    group = Group.objects.get(pk=settings.GROUPS.get('empleado'))
                    usuario.groups.add(group)
                                   
                    
                    #INSTANCIAR EMPLEADO
                    empleado = Empleado()
                    empleado.usuario = usuario
                    empleado.ci = isNULL(request.POST["ci"])
                    empleado.ruc = isNULL(request.POST["ruc"])
                    empleado.nombre = isNULL(request.POST["nombre"])
                    empleado.apellido = isNULL(request.POST["apellido"])
                    empleado.nacionalidad_id = isNULL(request.POST["nacionalidad"])
                    empleado.ciudad_id = isNULL(request.POST["ciudad"])
                    empleado.barrio_id = isNULL(request.POST["barrio"])
                    empleado.direccion = isNULL(request.POST["direccion"])
                    empleado.celular = isNULL(request.POST["celular"])
                    empleado.telefono = isNULL(request.POST["telefono"])
                    empleado.email = isNULL(request.POST["email"])
                    empleado.fec_nacimiento = YYYY_MM_DD(isNULL(request.POST["fec_nacimiento"]))
                    empleado.sexo_id = isNULL(request.POST["sexo"])
                    empleado.estado_civil_id = isNULL(request.POST["estado_civil"])                   
                    empleado.save()
                    data["id"] = empleado.id

                # data = self.get_form().save()
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_ciudad":
                data = []
                term = request.POST["term"]
                qs = Ciudad.objects.filter(
                    Q(activo__exact=True)
                    & (
                        Q(distrito__denominacion__icontains=term)
                        | Q(denominacion__icontains=term)
                    )
                ).order_by("denominacion", "distrito_id")[0:25]

                data = [{"id": "", "text": "------------"}]
                id_dpto_aux = 0
                for i in qs:
                    if id_dpto_aux != i.distrito_id:
                        data.append(
                            {
                                "text": str(i.distrito),
                                "children": [{"id": i.id, "text": str(i)}],
                            }
                        )
                    else:
                        data.append(
                            {
                                "children": [{"id": i.id, "text": str(i)}],
                            }
                        )
                    id_dpto_aux = i.distrito_id

            elif action == "search_barrio":
                data = [{"id": "", "text": "---------"}]
                ciudad_list = None
                if "id" in request.POST:
                    ciudad_list = [request.POST["id"] if "id" in request.POST else None]

                elif "id[]" in request.POST:
                    ciudad_list = (
                        request.POST.getlist("id[]") if "id[]" in request.POST else None
                    )
                if ciudad_list:
                    for i in Barrio.objects.filter(ciudad_id__in=ciudad_list):
                        data.append(
                            {"id": i.id, "text": str(i), "data": i.ciudad.toJSON()}
                        )
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Nuevo registro de un Empleado"
        context["action"] = "add"
        context["instance"] = None
        return context


class EmpleadoUpdate(PermissionMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleado/create.html"

    success_url = reverse_lazy("empleado_list")
    permission_required = "change_empleado"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            id = self.get_object().id
            if type == "ci":
                if Empleado.objects.filter(ci__iexact=obj).exclude(id=id):
                    data["valid"] = False
            if type == "ruc":
                if Empleado.objects.filter(ruc__iexact=obj).exclude(id=id):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "edit":
                with transaction.atomic():
                     #INSTANCIAR USUARIO
                    instance = self.object
                    usuario = instance.usuario
                    usuario.first_name = request.POST['nombre']
                    usuario.last_name = request.POST['apellido']
                    usuario.dni = request.POST['ci']
                    usuario.username = usuario.dni
                    if 'image-clear' in request.POST:
                        if usuario.image:
                            usuario.image.delete(save=False)
                        usuario.image = None
                    elif 'image' in request.FILES:
                        usuario.image = request.FILES['image']

                    usuario.email = request.POST['email']
                    usuario.save()                                        
                    group = Group.objects.get(pk=settings.GROUPS.get('empleado'))
                    usuario.groups.add(group) 

                    #INSTANCIAR EMPLEADO
                    empleado = instance
                    empleado.usuario_id = usuario.id
                    empleado.ci = isNULL(request.POST["ci"])
                    empleado.ruc = isNULL(request.POST["ruc"])
                    empleado.nombre = isNULL(request.POST["nombre"])
                    empleado.apellido = isNULL(request.POST["apellido"])
                    empleado.nacionalidad_id = isNULL(request.POST["nacionalidad"])
                    empleado.ciudad_id = isNULL(request.POST["ciudad"])
                    empleado.barrio_id = isNULL(request.POST["barrio"])
                    empleado.direccion = isNULL(request.POST["direccion"])
                    empleado.celular = isNULL(request.POST["celular"])
                    empleado.telefono = isNULL(request.POST["telefono"])
                    empleado.email = isNULL(request.POST["email"])
                    empleado.fec_nacimiento = YYYY_MM_DD(isNULL(request.POST["fec_nacimiento"]))
                    empleado.sexo_id = isNULL(request.POST["sexo"])
                    empleado.estado_civil_id = isNULL(request.POST["estado_civil"])                   
                    empleado.save()
                    data["id"] = empleado.id

            elif action == "validate_data":
                return self.validate_data()
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Edición de un Empleado"
        context["action"] = "edit"
        context["instance"] = self.object
        return context


class EmpleadoDelete(PermissionMixin, DeleteView):
    model = Empleado
    template_name = "empleado/delete.html"
    success_url = reverse_lazy("empleado_list")
    permission_required = "delete_empleado"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Notificación de eliminación"
        context["list_url"] = self.success_url
        return context


class EmpleadoUpdatePerfil(UpdateView):
    # class EmpleadoUpdatePerfil(PermissionMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleado/create.html"
    success_url = reverse_lazy("dashboard")
    permission_required = "change_empleado"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    # # Sobrescribir get_success_url para redirigir a la misma página
    # def get_success_url(self):
    #     return self.request.path

    # Obtener empleado asociado al usuario logueado
    def get_empleado(self):
        try:
            return Empleado.objects.get(usuario=self.request.user)
        except Empleado.DoesNotExist:
            raise Http404("No se encontró el perfil del empleado asociado al usuario.")

    # Sobrescribir get_object para obtener el empleado del usuario logueado
    def get_object(self, queryset=None):
        empleado = self.get_empleado()
        if empleado:
            return empleado
        return Empleado()
    
    # Validar datos únicos
    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            id = self.get_object().id
            if type == "ci":
                if Empleado.objects.filter(ci__iexact=obj).exclude(id=id):
                    data["valid"] = False
            if type == "ruc":
                if Empleado.objects.filter(ruc__iexact=obj).exclude(id=id):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get("action")
        try:
            if action == "edit":
                with transaction.atomic():
                    empleado = self.get_object()
                    usuario = empleado.usuario

                    # Actualizar datos del usuario
                    usuario.first_name = request.POST.get("nombre", "").strip()
                    usuario.last_name = request.POST.get("apellido", "").strip()
                    usuario.dni = request.POST.get("ci", "").strip()
                    usuario.username = usuario.dni
                    usuario.email = request.POST.get("email", "").strip()

                    # Manejo de imagen
                    if "image-clear" in request.POST:
                        if usuario.image:
                            usuario.image.delete(save=False)
                        usuario.image = None
                    if "image" in request.FILES:
                        usuario.image = request.FILES["image"]

                    usuario.save()

                    # Asignar grupo si no está
                    group = Group.objects.get(pk=settings.GROUPS.get("empleado"))
                    usuario.groups.add(group)

                    # Actualizar datos del empleado
                    empleado.ci = isNULL(request.POST.get("ci"))
                    empleado.ruc = isNULL(request.POST.get("ruc"))
                    empleado.nombre = isNULL(request.POST.get("nombre"))
                    empleado.apellido = isNULL(request.POST.get("apellido"))
                    empleado.nacionalidad_id = isNULL(request.POST.get("nacionalidad"))
                    empleado.ciudad_id = isNULL(request.POST.get("ciudad"))
                    empleado.barrio_id = isNULL(request.POST.get("barrio"))
                    empleado.direccion = isNULL(request.POST.get("direccion"))
                    empleado.celular = isNULL(request.POST.get("celular"))
                    empleado.telefono = isNULL(request.POST.get("telefono"))
                    empleado.email = isNULL(request.POST.get("email"))
                    empleado.fec_nacimiento = YYYY_MM_DD(isNULL(request.POST.get("fec_nacimiento")))
                    empleado.sexo_id = isNULL(request.POST.get("sexo"))
                    empleado.estado_civil_id = isNULL(request.POST.get("estado_civil"))
                    empleado.save()

                    data["id"] = empleado.id

            elif action == "validate_data":
                return self.validate_data()
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = f" Perfil de {self.object.nombre} {self.object.apellido}"
        context["action"] = "edit"
        context["instance"] = self.object
        return context