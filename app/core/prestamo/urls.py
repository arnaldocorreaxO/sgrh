from django.urls import path

from core.base.views.transaccion.views import TransaccionFormView
from core.prestamo.views.prestamo.views import *

# from core.prestamo.views.prestamo.views import *
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
    path(
        "transaccion/",
        TransaccionPrestamoFormView.as_view(),
        name="trx_prestamo_create",
    ),
    path(
        "trx503/",
        Trx503.as_view(),
        name="trx503_create",
    ),
    path(
        "trx504/",
        Trx504.as_view(),
        name="trx504_create",
    ),
]
