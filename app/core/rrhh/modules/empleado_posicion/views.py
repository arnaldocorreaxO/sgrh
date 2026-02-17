import json
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView,DeleteView
from datetime import datetime

from core.base.views.generics import BaseListView
from core.rrhh.models import Dependencia, DependenciaPosicion, EmpleadoPosicion
from core.rrhh.modules.empleado.forms import EmpleadoFilterForm
from core.rrhh.modules.empleado_posicion.forms import EmpleadoPosicionFilterForm, EmpleadoPosicionForm # Asumiendo esta ruta
from core.rrhh.modules.empleado.views import EmpleadoScopedMixin
from core.security.mixins import PermissionMixin

class EmpleadoPosicionList(PermissionMixin, EmpleadoScopedMixin, BaseListView):
    model = EmpleadoPosicion
    context_prefix = "Asignación de Cargo/Puesto"
    create_url_name = "empleado_posicion_create"
    permission_required = "view_empleadoposicion"
    template_name = 'empleado_posicion/list.html'
    
    search_fields = ["empleado__nombre", "empleado__apellido", 
                     "dependencia_posicion__dependencia__denominacion", 
                     "dependencia_posicion__posicion__denominacion"]
    numeric_fields = ["id", "empleado_id","legajo"]
    default_order_fields = ["-fecha_inicio"]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        sucursal_id = self.request.POST.get("sucursal")
        empleado_id = self.request.POST.get("empleado")
        dependencia_padre_id = self.request.POST.get("dependencia_padre")
        dependencia_hija_id = self.request.POST.get("dependencia_hija")

        tipo_movimiento = self.request.POST.get("tipo_movimiento")
        rango_fecha = self.request.POST.get("rango_fecha")

        print("Filters - Sucursal:", sucursal_id, 
              "Empleado:", empleado_id, 
              "Dependencia Padre:", dependencia_padre_id, 
              "Dependencia Hija:", dependencia_hija_id, 
              "Tipo Movimiento:", tipo_movimiento, 
              "Rango Fecha:", rango_fecha)

        if not self.is_self_view:
            # Validamos que exista al menos un filtro
            if not any([sucursal_id, empleado_id, tipo_movimiento,dependencia_padre_id, dependencia_hija_id, rango_fecha]):
                return self.model.objects.none()
            
            if sucursal_id:
                qs = qs.filter(dependencia_posicion__dependencia__sucursal_institucion__sucursal_id=sucursal_id)
               
            
            if empleado_id:
                qs = qs.filter(empleado_id=empleado_id)
      

            if dependencia_padre_id:
                qs = qs.filter(dependencia_posicion__dependencia__dependencia_padre=dependencia_padre_id)
                
            
            if dependencia_hija_id:
                qs = qs.filter(dependencia_posicion__dependencia_id=dependencia_hija_id) 
         

            if tipo_movimiento:
                qs = qs.filter(tipo_movimiento=tipo_movimiento)

        # Filtro de rango de fechas (Flatpickr)
        if 1==0:
            if rango_fecha and " a " in rango_fecha:
                try:
                    f_desde_str, f_hasta_str = rango_fecha.split(" a ")
                    f_desde = datetime.strptime(f_desde_str.strip(), '%d/%m/%Y').date()
                    f_hasta = datetime.strptime(f_hasta_str.strip(), '%d/%m/%Y').date()
                    qs = qs.filter(fecha_inicio__range=[f_desde, f_hasta])
                except (ValueError, IndexError):
                    print("Error parsing date range:", rango_fecha)
                    pass

        return qs.select_related("empleado", "dependencia_posicion", "tipo_movimiento", "vinculo_laboral")

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get("action", "")
        try:
            if action == "search":
                data = self.handle_search(request)
            else:
                data["error"] = "No ha ingresado una opción válida"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(data, content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy(self.create_url_name + ("_self" if self.is_self_view else ""))
        if not self.is_self_view:
            context["title"] = "Listado de " + self.context_prefix
            context["empleado_filter_form"] = EmpleadoFilterForm(self.request.GET or None, user=self.request.user)
            context["empleado_posicion_filter_form"] = EmpleadoPosicionFilterForm(self.request.GET or None)
        else:
            context = self.enrich_context_with_empleado(context, prefijo=self.context_prefix)
        return context

class EmpleadoPosicionCreate(PermissionMixin,  CreateView):
    model = EmpleadoPosicion
    form_class = EmpleadoPosicionForm
    template_name = "empleado_posicion/create.html"
    permission_required = "add_empleadoposicion"
    success_url = reverse_lazy("empleado_posicion_list")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get("action", "add")
            if action == "add":
                form = self.get_form()
                if form.is_valid():
                    form.save()
                else:
                    data["error"] = form.errors

            elif action == "validate_data":
                return self.validate_data()
            
            elif action == "search_dependencia_padre":
                term = request.POST.get("term", "")
                print("Term:", term)
                dependencia_padre = Dependencia.search(term)				
                data = [{"id": dependencia.id, "text": str(dependencia)} for dependencia in dependencia_padre]
            
            elif action == "search_dependencia_hija":
                padre_id = request.POST.get("padre_id", "")
                term = request.POST.get("term", "")
                print("Term:", term)
                dependencia_padre = Dependencia.search(padre_id=padre_id, term=term)				
                data = [{"id": dependencia.id, "text": str(dependencia)} for dependencia in dependencia_padre]
            
            elif action == "search_dependencia_posicion":
                term = request.POST.get("term", "")
                print("Term:", term)
                dependencias_posiciones = DependenciaPosicion.search(term)				
                data = [{"id": dependencia_posicion.id, "text": str(dependencia_posicion)} for dependencia_posicion in dependencias_posiciones]

        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["action"] = "add"
        context["title"] = "Nueva Asignación de Cargo"
        return context
    
class EmpleadoPosicionUpdate(PermissionMixin, UpdateView):
    model = EmpleadoPosicion
    form_class = EmpleadoPosicionForm
    template_name = "empleado_posicion/create.html"
    permission_required = "change_empleadoposicion"
    success_url = reverse_lazy("empleado_posicion_list")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)       

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get("action", "")
        try:
            if action == "edit":
                obj = self.get_object()
                form = self.form_class(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    form.save() # El modelo gestiona la lógica de legajo y exclusividad
                else:
                    data["error"] = form.errors
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
        context["action"] = "edit"
        context["instance"] = self.object
        context["title"] = "Modificar Asignación de Cargo"
        return context
    
class EmpleadoPosicionDelete(PermissionMixin, EmpleadoScopedMixin, DeleteView):
    model = EmpleadoPosicion
    template_name = "posicion/delete.html"
    permission_required = "delete_empleadoposicion"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return self.get_success_url_for("empleado_posicion_list")

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
        context["list_url"] = self.get_success_url()
        return context