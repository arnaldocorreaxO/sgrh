from django.urls import path

from core.prestamo.views.prestamo.views import *
from core.prestamo.views.solicitud_prestamo.views import *

urlpatterns = [
    # SOLICITUD DE PRESTAMO
    path(
        "solicitud_prestamo",
        SolicitudPrestamoList.as_view(),
        name="solicitud_prestamo_list",
    ),
    path(
        "solicitud_prestamo/add/",
        SolicitudPrestamoCreate.as_view(),
        name="solicitud_prestamo_create",
    ),
    path(
        "solicitud_prestamo/update/<int:pk>/",
        SolicitudPrestamoUpdate.as_view(),
        name="solicitud_prestamo_update",
    ),
    # path(
    #     "solicitud_prestamo/aprobar/<int:pk>/",
    #     AprobarSolicitudPrestamoUpdate.as_view(),
    #     name="solicitud_prestamo_aprobar",
    # ),
    path(
        "solicitud_prestamo/delete/<int:pk>/",
        SolicitudPrestamoDelete.as_view(),
        name="solicitud_prestamo_delete",
    ),
    # SOCIO
    # path("socio", SocioList.as_view(), name="socio_list"),
    # path("socio/add/", SocioCreate.as_view(), name="socio_create"),
    # path("socio/update/<int:pk>/", SocioUpdate.as_view(), name="socio_update"),
    # path("socio/delete/<int:pk>/", SocioDelete.as_view(), name="socio_delete"),
]
