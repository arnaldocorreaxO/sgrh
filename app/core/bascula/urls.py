from core.bascula.views.bascula.movimiento.views import *
from core.bascula.views.bascula.transporte.views import *
from core.bascula.views.bascula.cliente.views import *
from core.bascula.views.bascula.categoria.views import *
from core.bascula.views.bascula.producto.views import *
from core.bascula.views.bascula.clienteproducto.views import *
from core.bascula.views.bascula.marcavehiculo.views import *
from core.bascula.views.bascula.vehiculo.views import *
from core.bascula.views.bascula.chofer.views import *

from django.urls import path

urlpatterns = [    
    # URL para lectura de Puerto COM
	path('ajax_puerto_serial/<str:puerto>/',leer_puerto_serial,name='leer_puerto_serial'),
	path('ajax_peso_bascula/',leer_peso_bascula,name='leer_peso_bascula'),

    # MOVIMIENTO BASCULA
    path('movimiento', MovimientoList.as_view(), name='movimiento_list'),
    path('movimiento/add/', MovimientoCreate.as_view(), name='movimiento_create'),
    path('movimiento/update/<int:pk>/<tipo_salida>/', MovimientoUpdateSalida.as_view(), name='movimiento_update_salida'),    
    path('movimiento/update/<int:pk>/', MovimientoUpdate.as_view(), name='movimiento_update'),
    path('movimiento/delete/<int:pk>/', MovimientoDelete.as_view(), name='movimiento_delete'),
    path('movimiento/print/<int:pk>/', MovimientoPrint.as_view(), name='movimiento_print'),
    # TRANSPORTE
    path('transporte', TransporteList.as_view(), name='transporte_list'),
    path('transporte/add/', TransporteCreate.as_view(), name='transporte_create'),
    path('transporte/update/<int:pk>/', TransporteUpdate.as_view(), name='transporte_update'),
    path('transporte/delete/<int:pk>/', TransporteDelete.as_view(), name='transporte_delete'),
    # CLIENTE
    path('cliente', ClienteList.as_view(), name='cliente_list'),
    path('cliente/add/', ClienteCreate.as_view(), name='cliente_create'),
    path('cliente/update/<int:pk>/', ClienteUpdate.as_view(), name='cliente_update'),
    path('cliente/delete/<int:pk>/', ClienteDelete.as_view(), name='cliente_delete'),
    # CATEGORIA
    path('categoria', CategoriaList.as_view(), name='categoria_list'),
    path('categoria/add/', CategoriaCreate.as_view(), name='categoria_create'),
    path('categoria/update/<int:pk>/', CategoriaUpdate.as_view(), name='categoria_update'),
    path('categoria/delete/<int:pk>/', CategoriaDelete.as_view(), name='categoria_delete'),
    # PRODUCTO
    path('producto', ProductoList.as_view(), name='producto_list'),
    path('producto/add/', ProductoCreate.as_view(), name='producto_create'),
    path('producto/update/<int:pk>/', ProductoUpdate.as_view(), name='producto_update'),
    path('producto/delete/<int:pk>/', ProductoDelete.as_view(), name='producto_delete'),
    # CLIENTE PRODUCTO
    path('clienteproducto', ClienteProductoList.as_view(), name='clienteproducto_list'),
    path('clienteproducto/add/', ClienteProductoCreate.as_view(), name='clienteproducto_create'),
    path('clienteproducto/update/<int:pk>/', ClienteProductoUpdate.as_view(), name='clienteproducto_update'),
    path('clienteproducto/delete/<int:pk>/', ClienteProductoDelete.as_view(), name='clienteproducto_delete'),
    # MARCA VEHICULO
    path('marcavehiculo', MarcaVehiculoList.as_view(), name='marcavehiculo_list'),
    path('marcavehiculo/add/', MarcaVehiculoCreate.as_view(), name='marcavehiculo_create'),
    path('marcavehiculo/update/<int:pk>/', MarcaVehiculoUpdate.as_view(), name='marcavehiculo_update'),
    path('marcavehiculo/delete/<int:pk>/', MarcaVehiculoDelete.as_view(), name='marcavehiculo_delete'),
    # VEHICULO
    path('vehiculo', VehiculoList.as_view(), name='vehiculo_list'),
    path('vehiculo/add/', VehiculoCreate.as_view(), name='vehiculo_create'),
    path('vehiculo/update/<int:pk>/', VehiculoUpdate.as_view(), name='vehiculo_update'),
    path('vehiculo/delete/<int:pk>/', VehiculoDelete.as_view(), name='vehiculo_delete'),
    # CHOFER
    path('chofer', ChoferList.as_view(), name='chofer_list'),
    path('chofer/add/', ChoferCreate.as_view(), name='chofer_create'),
    path('chofer/update/<int:pk>/', ChoferUpdate.as_view(), name='chofer_update'),
    path('chofer/delete/<int:pk>/', ChoferDelete.as_view(), name='chofer_delete'),

   ]
