from django.urls import path

from core.rrhh.empleado.views import *
from core.rrhh.formacion_academica.views import *
from core.rrhh.capacitacion.views import *
from core.rrhh.experiencia_laboral.views import *
from core.rrhh.documento_complementario.views import *
from core.rrhh.historico_disciplinario.views import *

urlpatterns = [
    # EMPLEADO
    # Vista general (admin)
    path("empleado/", EmpleadoList.as_view(), name="empleado_list"),
    path("empleado/add/", EmpleadoCreate.as_view(), name="empleado_create"),
    path("empleado/update/<int:pk>/", EmpleadoUpdate.as_view(), name="empleado_update"),    
    path("empleado/delete/<int:pk>/", EmpleadoDelete.as_view(), name="empleado_delete"),
    # Vista personal (empleado)
    path("empleado/self/", EmpleadoList.as_view(), name="empleado_list_self"),
    path("empleado/self/add/", EmpleadoCreate.as_view(), name="empleado_create_self"),
    path("empleado/self/update/", EmpleadoUpdate.as_view(), name="empleado_update_self"),    
    path("empleado/self/delete/", EmpleadoDelete.as_view(), name="empleado_delete_self"), 

    path("empleado/get_datos_persona/", get_datos_persona, name="get_datos_persona"),

    # CV EMPLEADO
    path('empleado/cv/pdf/<int:pk>/', CVEmpleadoPDFView.as_view(), name='cv_empleado_pdf'),
    path('empleado/self/cv/pdf/', CVEmpleadoPDFView.as_view(), name='cv_empleado_pdf_self'),
    
    # FORMACION
   # Vista general (admin)
    path("formacion_academica/", FormacionAcademicaList.as_view(), name="formacion_academica_list"),
    path("formacion_academica/add/", FormacionAcademicaCreate.as_view(), name="formacion_academica_create"),
    path("formacion_academica/update/<int:pk>/", FormacionAcademicaUpdate.as_view(), name="formacion_academica_update"),
    path("formacion_academica/delete/<int:pk>/", FormacionAcademicaDelete.as_view(), name="formacion_academica_delete"),

    # Vista personal (empleado)
    path("formacion_academica/self/", FormacionAcademicaList.as_view(), name="formacion_academica_list_self"),
    path("formacion_academica/self/add/", FormacionAcademicaCreate.as_view(), name="formacion_academica_create_self"),
    path("formacion_academica/self/update/<int:pk>/", FormacionAcademicaUpdate.as_view(), name="formacion_academica_update_self"),
    path("formacion_academica/self/delete/<int:pk>/", FormacionAcademicaDelete.as_view(), name="formacion_academica_delete_self"),    
   
    # OTROS ESTUDIOS 
    # Vista general (admin)
    path("capacitacion/", CapacitacionList.as_view(), name="capacitacion_list"),    
    path("capacitacion/add/", CapacitacionCreate.as_view(), name="capacitacion_create"),
    path("capacitacion/update/<int:pk>/", CapacitacionUpdate.as_view(), name="capacitacion_update"),
    path("capacitacion/delete/<int:pk>/", CapacitacionDelete.as_view(), name="capacitacion_delete"),
    # Vista personal (empleado)
    path("capacitacion/self/", CapacitacionList.as_view(), name="capacitacion_list_self"),    
    path("capacitacion/self/add/", CapacitacionCreate.as_view(), name="capacitacion_create_self"),
    path("capacitacion/self/update/<int:pk>/", CapacitacionUpdate.as_view(), name="capacitacion_update_self"),
    path("capacitacion/self/delete/<int:pk>/", CapacitacionDelete.as_view(), name="capacitacion_delete_self"),

    # EXPERENCIA LABORAL
    # Vista general (admin)
    path("experiencia_laboral/", ExperienciaLaboralList.as_view(), name="experiencia_laboral_list"),    
    path("experiencia_laboral/add/", ExperienciaLaboralCreate.as_view(), name="experiencia_laboral_create"),
    path("experiencia_laboral/update/<int:pk>/", ExperienciaLaboralUpdate.as_view(), name="experiencia_laboral_update"),
    path("experiencia_laboral/delete/<int:pk>/", ExperienciaLaboralDelete.as_view(), name="experiencia_laboral_delete"),
    # Vista personal (empleado)
    path("experiencia_laboral/self/", ExperienciaLaboralList.as_view(), name="experiencia_laboral_list_self"),    
    path("experiencia_laboral/self/add/", ExperienciaLaboralCreate.as_view(), name="experiencia_laboral_create_self"),
    path("experiencia_laboral/self/update/<int:pk>/", ExperienciaLaboralUpdate.as_view(), name="experiencia_laboral_update_self"),
    path("experiencia_laboral/self/delete/<int:pk>/", ExperienciaLaboralDelete.as_view(), name="experiencia_laboral_delete_self"),
    
    # DOCUMENTOS COMPLEMENTARIOS
    # Vista general (admin)
    path("documento_complementario/", DocumentoComplementarioList.as_view(), name="documento_complementario_list"),    
    path("documento_complementario/add/", DocumentoComplementarioCreate.as_view(), name="documento_complementario_create"),
    path("documento_complementario/update/<int:pk>/", DocumentoComplementarioUpdate.as_view(), name="documento_complementario_update"),
    path("documento_complementario/delete/<int:pk>/", DocumentoComplementarioDelete.as_view(), name="documento_complementario_delete"),
    # Vista personal (empleado)
    path("documento_complementario/self/", DocumentoComplementarioList.as_view(), name="documento_complementario_list_self"),    
    path("documento_complementario/self/add/", DocumentoComplementarioCreate.as_view(), name="documento_complementario_create_self"),
    path("documento_complementario/self/update/<int:pk>/", DocumentoComplementarioUpdate.as_view(), name="documento_complementario_update_self"),
    path("documento_complementario/self/delete/<int:pk>/", DocumentoComplementarioDelete.as_view(), name="documento_complementario_delete_self"),
    
    # HISTORICO DISCIPLINARIO
    # Vista general (admin)
    path("historico_disciplinario/", HistoricoDisciplinarioList.as_view(), name="historico_disciplinario_list"),    
    path("historico_disciplinario/add/", HistoricoDisciplinarioCreate.as_view(), name="historico_disciplinario_create"),
    path("historico_disciplinario/update/<int:pk>/", HistoricoDisciplinarioUpdate.as_view(), name="historico_disciplinario_update"),
    path("historico_disciplinario/delete/<int:pk>/", HistoricoDisciplinarioDelete.as_view(), name="historico_disciplinario_delete"),
    # Vista personal (empleado)
    path("historico_disciplinario/self/", HistoricoDisciplinarioList.as_view(), name="historico_disciplinario_list_self"),    
    path("historico_disciplinario/self/add/", HistoricoDisciplinarioCreate.as_view(), name="historico_disciplinario_create_self"),
    path("historico_disciplinario/self/update/<int:pk>/", HistoricoDisciplinarioUpdate.as_view(), name="historico_disciplinario_update_self"),
    path("historico_disciplinario/self/delete/<int:pk>/", HistoricoDisciplinarioDelete.as_view(), name="historico_disciplinario_delete_self"),




]