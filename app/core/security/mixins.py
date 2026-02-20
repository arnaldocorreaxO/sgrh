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

