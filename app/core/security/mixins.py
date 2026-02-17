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
debug = settings.DEBUG
class PermissionMixin(object):
    permission_required = None

    def is_self_url_view(self):
        return self.request.resolver_match.url_name.endswith("_self")

    def get_permits(self):
        if not self.permission_required:
            return []
        perms = [self.permission_required] if isinstance(self.permission_required, str) else list(self.permission_required)
        
        if self.is_self_url_view():
            scoped_perms = []
            for p in perms:
                app_label, codename = p.split(".") if "." in p else (None, p)
                new_p = f"{app_label}.{codename}_self" if app_label else f"{codename}_self"
                scoped_perms.append(new_p)
            return scoped_perms
        return perms

    def get_last_url(self):
        request = get_current_request()
        return request.session.get("url_last", settings.LOGIN_REDIRECT_URL)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        from core.rrhh.models import Empleado
        request.session["module"] = None
        try:
            # 1. Superusuarios: Acceso total
            if request.user.is_superuser:
                if debug: print("DEBUG - Acceso: Superusuario detectado.")
                return super().dispatch(request, *args, **kwargs)

            # 2. Obtener Grupo y Permisos
            group = request.session.get("group")
            permits = self.get_permits()
            is_self = self.is_self_url_view()

            if not group or not permits:
                if debug: print(f"DEBUG - Acceso Denegado: Grupo ({group}) o Permisos ({permits}) faltantes.")
                return HttpResponseRedirect(self.get_last_url())

            # 3. Validación de Permisos de Base (Database)
            for p in permits:
                codename = p.split(".")[-1]
                if not group.grouppermission_set.filter(permission__codename=codename).exists():
                    if debug: print(f"DEBUG - Acceso Denegado: Grupo {group.name} no tiene el permiso {codename}")
                    messages.error(request, "No tiene permiso para ingresar a este módulo")
                    return HttpResponseRedirect(self.get_last_url())

            # ----------------------------------------------------------------
            # 4. LÓGICA DE JERARQUÍA (ADMIN_RRHH_SUCURSAL / GLOBAL / SELF)
            # ----------------------------------------------------------------
            user_empleado = getattr(request.user, 'empleado', None)
            
            # Si la vista requiere un objeto (Update, Detail, PDF), lo obtenemos para validar
            pk_target = kwargs.get('pk')
            
            if is_self:
                if debug: print("DEBUG - Validando Perfil Propio (is_self).")
                # En is_self, el objeto SIEMPRE debe ser el del usuario logueado
                # Si hay un PK en la URL que no es el suyo, se bloquea por lógica de get_object en la vista
                pass 

            elif group.name == "ADMIN_RRHH_SUCURSAL":
                if pk_target and user_empleado:
                    target_obj = Empleado.objects.filter(pk=pk_target).first()
                    if target_obj and target_obj.sucursal != user_empleado.sucursal:
                        if debug: print(f"DEBUG - Bloqueo Sucursal: Admin {user_empleado.sucursal} intentó ver {target_obj.sucursal}")
                        messages.error(request, "Acceso denegado: El empleado pertenece a otra sucursal.")

                        last_url = self.get_last_url()
                        if debug: print(f"DEBUG - Redirigiendo a última URL: {last_url}")
                        if last_url == request.path:
                            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)                        
                        return HttpResponseRedirect(self.get_last_url())
                if debug: print("DEBUG - Acceso Sucursal: OK.")

            elif group.name == "ADMIN_RRHH_GLOBAL":
                if debug: print("DEBUG - Acceso Global: OK (Independiente de sucursal).")

            # 5. Registro de rastro y éxito
            first_codename = permits[0].split(".")[-1]
            grouppermission = group.grouppermission_set.filter(permission__codename=first_codename).first()
            if grouppermission:
                request.session["url_last"] = request.path
                request.session["module"] = grouppermission.module
            
            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            if debug: print(f"DEBUG - Error Crítico en PermissionMixin: {str(e)}")
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

# class PermissionMixin(object):
#     permission_required = None  # Ej: "add_empleado"

#     def is_self_url_view(self):
#         return self.request.resolver_match.url_name.endswith("_self")

#     def get_permits(self):
#         """Devuelve la lista de permisos requeridos, adaptando a _self si corresponde"""
#         if not self.permission_required:
#             return []

#         perms = [self.permission_required] if isinstance(self.permission_required, str) else list(self.permission_required)
        
#         if debug: print(f"DEBUG - Permisos base detectados: {perms}")
        
#         if self.is_self_url_view():
#             scoped_perms = []
#             for p in perms:
#                 if "." in p:
#                     app_label, codename = p.split(".")
#                     scoped_perms.append(f"{app_label}.{codename}_self")
#                 else:
#                     scoped_perms.append(f"{p}_self")
#             if debug: print(f"DEBUG - Vista personal detectada (_self). Scoped perms: {scoped_perms}")
#             return scoped_perms
            
#         if debug: print(f"DEBUG - Vista administrativa detectada. Permisos: {perms}")
#         return perms    

#     def get_last_url(self):
#         request = get_current_request()
#         if debug: print(f"DEBUG - Última URL en sesión: {request.session.get('url_last')}")
#         return request.session.get("url_last", settings.LOGIN_REDIRECT_URL)

#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         """
#         Validación de seguridad ejecutada al inicio de cualquier petición (GET/POST/PDF).
#         """
#         request.session["module"] = None
#         try:
#             # 1. Superusuarios acceso total
#             if request.user.is_superuser:
#                 if debug: print("DEBUG - Acceso concedido: Usuario es superusuario.")
#                 return super().dispatch(request, *args, **kwargs)
            
#             # 2. Validación por Grupos
#             if "group" in request.session:
#                 group = request.session["group"]
#                 permits = self.get_permits()

#                 if debug: print(f"DEBUG - Grupo en sesión: {group}")
#                 if debug: print(f"DEBUG - Permisos a validar: {permits}")

#                 if not permits:
#                     if debug: print("DEBUG - Alerta: No se definieron permisos en la vista (permission_required = None).")
#                     return super().dispatch(request, *args, **kwargs)

#                 for p in permits:
#                     codename = p.split(".")[-1]
#                     if debug: print(f"DEBUG - Verificando en DB codename: {codename}")
                    
#                     if not group.grouppermission_set.filter(permission__codename=codename).exists():
#                         if debug: print(f"DEBUG - ACCESO DENEGADO: El grupo {group} no tiene el permiso {codename}")
#                         messages.error(request, "No tiene permiso para ingresar a este módulo")
#                         return HttpResponseRedirect(self.get_last_url())

#                 # 3. Guardar rastro del módulo y URL si todo está OK
#                 first_codename = permits[0].split(".")[-1]
#                 grouppermission = group.grouppermission_set.filter(permission__codename=first_codename)
                
#                 if grouppermission.exists():
#                     request.session["url_last"] = request.path
#                     request.session["module"] = grouppermission[0].module
#                     if debug: print(f"DEBUG - Acceso exitoso. Módulo: {request.session['module']} | URL: {request.path}")

#                 return super().dispatch(request, *args, **kwargs)
            
#             if debug: print("DEBUG - ACCESO DENEGADO: No existe un grupo activo en la sesión.")
#             return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

#         except Exception as e:
#             if debug: print(f"DEBUG - ERROR CRÍTICO en PermissionMixin: {str(e)}")
#             return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

# ORIGINAL XO
# class PermissionMixin(object):
#     permission_required = None  # Ej: "add_empleado"

#     # Detecta si la vista es personal (_self) o administrativa que se determina por el nombre de la URL
#     def is_self_url_view(self):
#         return self.request.resolver_match.url_name.endswith("_self")

#     def get_permits(self):
#         """Devuelve la lista de permisos requeridos, adaptando a _self si corresponde"""
#         if not self.permission_required:
#             return []

#         perms = [self.permission_required] if isinstance(self.permission_required, str) else list(self.permission_required)
#         if debug: print("Permisos base:", perms)
#         if self.is_self_url_view():
#             scoped_perms = []
#             for p in perms:
#                 if "." in p:
#                     app_label, codename = p.split(".")
#                     scoped_perms.append(f"{app_label}.{codename}_self")
#                 else:
#                     scoped_perms.append(f"{p}_self")
#             return scoped_perms
#         if debug: print("Permisos sin modificar:", perms)
#         return perms    

#     def get_last_url(self):
#         request = get_current_request()
#         if debug: print(request.session.get("url_last"))
#         return request.session.get("url_last", settings.LOGIN_REDIRECT_URL)

#     @method_decorator(login_required)
#     def get(self, request, *args, **kwargs):
#         request.session["module"] = None
#         try:
#             # Superusuarios tienen acceso total
#             if request.user.is_superuser:
#                 if debug: print("Usuario es superusuario, acceso total")
#                 return super().get(request, *args, **kwargs)
            
#             if "group" in request.session:
#                 group = request.session["group"]
#                 # Obtener permisos requeridos para esta vista adaptados a _self si aplica
#                 permits = self.get_permits()
#                 if debug: print("Grupo:", group)
#                 if debug: print("Permisos requeridos:", permits)
#                 for p in permits:
#                     codename = p.split(".")[-1]
#                     if debug: print("Verificando permiso:", codename)
#                     if not group.grouppermission_set.filter(permission__codename=codename).exists():
#                         messages.error(request, "No tiene permiso para ingresar a este módulo")
#                         return HttpResponseRedirect(self.get_last_url())

#                 # Guardar módulo y URL actual
#                 codename = permits[0].split(".")[-1]
#                 grouppermission = group.grouppermission_set.filter(permission__codename=codename)
#                 if debug: print("Permisos del grupo:", grouppermission)
#                 if grouppermission.exists():
#                     request.session["url_last"] = request.path
#                     if debug: print("URL última:", request.session["url_last"])
#                     request.session["module"] = grouppermission[0].module

#                 return super().get(request, *args, **kwargs)
#         except Exception as e:
#             print("Error en permisos:", e)
#             return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)




# class PermissionMixin(object):
#     permission_required = None

#     def is_self_url_view(self):
#         return self.request.resolver_match.url_name.endswith("_self")

#     def get_permits(self):
#         if not self.permission_required:
#             return []
#         perms = [self.permission_required] if isinstance(self.permission_required, str) else list(self.permission_required)
#         if self.is_self_url_view():
#             scoped_perms = []
#             for p in perms:
#                 if "." in p:
#                     app_label, codename = p.split(".")
#                     scoped_perms.append(f"{app_label}.{codename}_self")
#                 else:
#                     scoped_perms.append(f"{p}_self")
#             return scoped_perms
#         return perms

#     def get_last_url(self):
#         request = get_current_request()
#         return request.session.get("url_last", settings.LOGIN_REDIRECT_URL)

#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         """
#         Se movió la lógica de get() a dispatch() para que valide 
#         antes de cualquier método (GET, POST, etc.)
#         """
#         request.session["module"] = None
#         try:
#             # 1. Superusuarios acceso total
#             if request.user.is_superuser:
#                 return super().dispatch(request, *args, **kwargs)
            
#             # 2. Validación por Grupos
#             if "group" in request.session:
#                 group = request.session["group"]
#                 permits = self.get_permits()

#                 # Si no hay permisos definidos, dejar pasar
#                 if not permits:
#                     return super().dispatch(request, *args, **kwargs)

#                 for p in permits:
#                     codename = p.split(".")[-1]
#                     if not group.grouppermission_set.filter(permission__codename=codename).exists():
#                         messages.error(request, "No tiene permiso para ingresar a este módulo")
#                         return HttpResponseRedirect(self.get_last_url())

#                 # 3. Guardar rastro del módulo si tiene éxito
#                 first_codename = permits[0].split(".")[-1]
#                 grouppermission = group.grouppermission_set.filter(permission__codename=first_codename)
                
#                 if grouppermission.exists():
#                     request.session["url_last"] = request.path
#                     request.session["module"] = grouppermission[0].module

#                 return super().dispatch(request, *args, **kwargs)
            
#             # Si no hay grupo en sesión, redirigir
#             return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

#         except Exception as e:
#             print("Error en permisos:", e)
#             return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)