from django.urls import path

from core.base.views.base.empresa.views import EmpresaUpdate
from core.base.views.base.sucursal.views import *

urlpatterns = [
    # EMPRESA
    path('empresa/update/', EmpresaUpdate.as_view(), name='empresa_update'),
    
     # SUCURSAL
    path('sucursal', SucursalList.as_view(), name='sucursal_list'),
    path('sucursal/add/', SucursalCreate.as_view(), name='sucursal_create'),
    path('sucursal/update/<int:pk>/', SucursalUpdate.as_view(), name='sucursal_update'),
    path('sucursal/delete/<int:pk>/', SucursalDelete.as_view(), name='sucursal_delete'),
    
]
