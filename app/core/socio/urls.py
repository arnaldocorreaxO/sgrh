from django.urls import path

from core.socio.views.socio.views import *
from core.socio.views.solicitud_ingreso.views import *

urlpatterns = [
    # SOLICITUD INGRESO
    path(
        "solicitud_ingreso",
        SolicitudIngresoList.as_view(),
        name="solicitud_ingreso_list",
    ),
    path(
        "solicitud_ingreso/add/",
        SolicitudIngresoCreate.as_view(),
        name="solicitud_ingreso_create",
    ),
    path(
        "solicitud_ingreso/update/<int:pk>/",
        SolicitudIngresoUpdate.as_view(),
        name="solicitud_ingreso_update",
    ),
    path(
        "solicitud_ingreso/aprobar/<int:pk>/",
        AprobarSolicitudIngresoUpdate.as_view(),
        name="solicitud_ingreso_aprobar",
    ),
    path(
        "solicitud_ingreso/delete/<int:pk>/",
        SolicitudIngresoDelete.as_view(),
        name="solicitud_ingreso_delete",
    ),
    # SOCIO
    path("socio", SocioList.as_view(), name="socio_list"),
    path("socio/add/", SocioCreate.as_view(), name="socio_create"),
    path("socio/update/<int:pk>/", SocioUpdate.as_view(), name="socio_update"),
    path("socio/delete/<int:pk>/", SocioDelete.as_view(), name="socio_delete"),
]
