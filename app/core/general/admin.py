from django.contrib import admin

from core.base.admin import ModeloAdminBase
from core.general.models import *

admin.site.register(TipoMovimiento, ModeloAdminBase)
admin.site.register(Plazo, ModeloAdminBase)
admin.site.register(CalificacionCliente, ModeloAdminBase)
admin.site.register(EstadoCliente, ModeloAdminBase)
