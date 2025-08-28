from django.urls import path

from core.base.views.empresa.views import EmpresaUpdate
from core.base.views.persona.views import *
from core.base.views.sucursal.views import *

urlpatterns = [
    # EMPRESA
    path("empresa/update/", EmpresaUpdate.as_view(), name="empresa_update"),
    # SUCURSAL
    path("sucursal", SucursalList.as_view(), name="sucursal_list"),
    path("sucursal/add/", SucursalCreate.as_view(), name="sucursal_create"),
    path("sucursal/update/<int:pk>/", SucursalUpdate.as_view(), name="sucursal_update"),
    path("sucursal/delete/<int:pk>/", SucursalDelete.as_view(), name="sucursal_delete"),
    # PERSONA
    path("persona", PersonaList.as_view(), name="persona_list"),
    path("persona/add/", PersonaCreate.as_view(), name="persona_create"),
    path("persona/update/<int:pk>/", PersonaUpdate.as_view(), name="persona_update"),
    path("persona/delete/<int:pk>/", PersonaDelete.as_view(), name="persona_delete"),
    path("persona/get_datos_persona/", get_datos_persona, name="get_datos_persona"),
   
]
