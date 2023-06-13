from django.urls import path

from core.caja.views.transaccion.views import *

urlpatterns = [
    path(
        "transaccion/add/",
        TransaccionCreateView.as_view(),
        name="transaccion_create",
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
]
