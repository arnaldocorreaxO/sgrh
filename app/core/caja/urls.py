from django.urls import path

from core.caja.views.movimiento.print.views import *
from core.caja.views.transaccion.views import *

urlpatterns = [
    path(
        "movimiento/",
        MovimientoListView.as_view(),
        name="movimiento_list",
    ),
    path(
        "transaccion/add/",
        TransaccionCajaFormView.as_view(),
        name="trx_caja_create",
    ),
    path(
        "trx700/add/",
        Trx700FormView.as_view(),
        name="trx700_create",
    ),
    path(
        "trx701/add/",
        Trx701FormView.as_view(),
        name="trx701_create",
    ),
    path(
        "trx702/add/",
        Trx702FormView.as_view(),
        name="trx702_create",
    ),
    path(
        "movimiento/print/<str:fec_movimiento>/<str:cod_movimiento>/<str:cod_cliente>/<str:cod_usuario>/",
        ReciboPrintView.as_view(),
        name="recibo_print",
    ),
]
