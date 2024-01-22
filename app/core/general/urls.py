from django.urls import path

from core.general.views.cliente.views import *

urlpatterns = [
    # CLIENTE
    path("cliente", ClienteList.as_view(), name="cliente_list"),
    path("cliente/add/", ClienteCreate.as_view(), name="cliente_create"),
    path("cliente/update/<int:pk>/", ClienteUpdate.as_view(), name="cliente_update"),
    path("cliente/delete/<int:pk>/", ClienteDelete.as_view(), name="cliente_delete"),
]
