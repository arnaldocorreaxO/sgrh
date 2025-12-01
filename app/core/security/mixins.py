from crum import get_current_request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator

from config import settings
from core.security.models import Module

class ModuleMixin(object):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        request.session['module'] = None
        try:
            request.user.set_group_session()
            group_id = request.user.get_group_id_session()
            modules = Module.objects.filter(Q(moduletype__is_active=True) | Q(moduletype__isnull=True)).filter(
                groupmodule__group_id__in=[group_id], is_active=True, url=request.path, is_visible=True)
            if modules.exists():
                request.session['module'] = modules[0]
                return super().get(request, *args, **kwargs)
            else:
                messages.error(request, 'No tiene permiso para ingresar a este módulo')
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        except:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

# Permisos requeridos para vistas administrativas y personales
# Se define un único permiso base (ej. 'add_formacionacademica')
# El sistema adapta automáticamente según el tipo de vista (_self)
# Ejemplo: 'add_formacionacademica' para vistas administrativas,
#          'add_formacionacademica_self' para vistas personales
# Los permisos personalizados deben definirse explícitamente en la clase Meta del modelo
debug = True
class PermissionMixin(object):
    permission_required = None  # Ej: "add_empleado"

    # Detecta si la vista es personal (_self) o administrativa que se determina por el nombre de la URL
    def is_self_url_view(self):
        return self.request.resolver_match.url_name.endswith("_self")

    def get_permits(self):
        """Devuelve la lista de permisos requeridos, adaptando a _self si corresponde"""
        if not self.permission_required:
            return []

        perms = [self.permission_required] if isinstance(self.permission_required, str) else list(self.permission_required)
        if debug: print("Permisos base:", perms)
        if self.is_self_url_view():
            scoped_perms = []
            for p in perms:
                if "." in p:
                    app_label, codename = p.split(".")
                    scoped_perms.append(f"{app_label}.{codename}_self")
                else:
                    scoped_perms.append(f"{p}_self")
            return scoped_perms
        if debug: print("Permisos sin modificar:", perms)
        return perms    

    def get_last_url(self):
        request = get_current_request()
        if debug: print(request.session.get("url_last"))
        return request.session.get("url_last", settings.LOGIN_REDIRECT_URL)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        request.session["module"] = None
        try:
            # Superusuarios tienen acceso total
            if request.user.is_superuser:
                if debug: print("Usuario es superusuario, acceso total")
                return super().get(request, *args, **kwargs)
            
            if "group" in request.session:
                group = request.session["group"]
                # Obtener permisos requeridos para esta vista adaptados a _self si aplica
                permits = self.get_permits()
                if debug: print("Grupo:", group)
                if debug: print("Permisos requeridos:", permits)
                for p in permits:
                    codename = p.split(".")[-1]
                    if debug: print("Verificando permiso:", codename)
                    if not group.grouppermission_set.filter(permission__codename=codename).exists():
                        messages.error(request, "No tiene permiso para ingresar a este módulo")
                        return HttpResponseRedirect(self.get_last_url())

                # Guardar módulo y URL actual
                codename = permits[0].split(".")[-1]
                grouppermission = group.grouppermission_set.filter(permission__codename=codename)
                if debug: print("Permisos del grupo:", grouppermission)
                if grouppermission.exists():
                    request.session["url_last"] = request.path
                    if debug: print("URL última:", request.session["url_last"])
                    request.session["module"] = grouppermission[0].module

                return super().get(request, *args, **kwargs)
        except Exception as e:
            print("Error en permisos:", e)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

# class PermissionMixin(object):
#     permission_required = None

#     def get_permits(self):
#         perms = []
#         if isinstance(self.permission_required, str):
#             perms.append(self.permission_required)
#         else:
#             perms = list(self.permission_required)
#         print(perms)
#         return perms

#     def get_last_url(self):
#         request = get_current_request()
#         if 'url_last' in request.session:
#             return request.session['url_last']
#         return settings.LOGIN_REDIRECT_URL

#     @method_decorator(login_required)
#     def get(self, request, *args, **kwargs):
#         request.session['module'] = None
#         try:
#             if 'group' in request.session:
#                 group = request.session['group']
#                 permits = self.get_permits()
#                 print(group)
#                 print(permits)
#                 for p in permits:
#                     if not group.grouppermission_set.filter(permission__codename=p).exists():
#                         print('ERROR')
#                         messages.error(request, 'No tiene permiso para ingresar a este módulo')
#                         return HttpResponseRedirect(self.get_last_url())
#                 grouppermission = group.grouppermission_set.filter(permission__codename=permits[0])
#                 print(grouppermission)
#                 if grouppermission.exists():
#                     request.session['url_last'] = request.path
#                     request.session['module'] = grouppermission[0].module
#                 return super().get(request, *args, **kwargs)
#         except:
#             return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
