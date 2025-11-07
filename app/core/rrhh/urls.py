from django.urls import path

from core.rrhh.views.empleado.views import *
from core.rrhh.views.formacion.views import *
from core.rrhh.views.capacitacion.views import *
from core.rrhh.views.experiencia.views import *
from core.rrhh.views.complementario.views import *
from core.rrhh.views.cv.views import CVEmpleadoView, CVEmpleadoPDFView

urlpatterns = [
    # EMPLEADO
    path("empleado", EmpleadoList.as_view(), name="empleado_list"),
    path("empleado/add/", EmpleadoCreate.as_view(), name="empleado_create"),
    path("empleado/update/<int:pk>/", EmpleadoUpdate.as_view(), name="empleado_update"),
    path("empleado/update/perfil", EmpleadoUpdatePerfil.as_view(), name="empleado_update_perfil"),
    path("empleado/delete/<int:pk>/", EmpleadoDelete.as_view(), name="empleado_delete"),
    path("empleado/get_datos_persona/", get_datos_persona, name="get_datos_persona"),
    
    # FORMACION
    path("formacion", FormacionList.as_view(), name="formacion_list"),
    path("formacion/add/", FormacionCreate.as_view(), name="formacion_create"),
    path("formacion/update/<int:pk>/", FormacionUpdate.as_view(), name="formacion_update"),
    path("formacion/delete/<int:pk>/", FormacionDelete.as_view(), name="formacion_delete"),
   
    # OTROS ESTUDIOS 
    path("capacitacion", CapacitacionList.as_view(), name="capacitacion_list"),
    path("capacitacion/add/", CapacitacionCreate.as_view(), name="capacitacion_create"),
    path("capacitacion/update/<int:pk>/", CapacitacionUpdate.as_view(), name="capacitacion_update"),
    path("capacitacion/delete/<int:pk>/", CapacitacionDelete.as_view(), name="capacitacion_delete"),
    
    # EXPERENCIA LABORAL
    path("experiencia", ExperienciaLaboralList.as_view(), name="experiencia_list"),
    path("experiencia/add/", ExperienciaLaboralCreate.as_view(), name="experiencia_create"),
    path("experiencia/update/<int:pk>/", ExperienciaLaboralUpdate.as_view(), name="experiencia_update"),
    path("experiencia/delete/<int:pk>/", ExperienciaLaboralDelete.as_view(), name="experiencia_delete"),
    
    # DOCUMENTOS COMPLEMENTARIOS
    path("complementario", DocumentoComplementarioList.as_view(), name="complementario_list"),
    path("complementario/add/", DocumentoComplementarioCreate.as_view(), name="complementario_create"),
    path("complementario/update/<int:pk>/", DocumentoComplementarioUpdate.as_view(), name="complementario_update"),
    path("complementario/delete/<int:pk>/", DocumentoComplementarioDelete.as_view(), name="complementario_delete"),
    
   # CV EMPLEADO
    path('cv/<int:pk>/', CVEmpleadoView.as_view(), name='cv_empleado'),
    path('cv/<int:pk>/pdf/', CVEmpleadoPDFView.as_view(), name='cv_empleado_pdf'),


]