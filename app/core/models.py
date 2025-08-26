from django.db import models
from crum import get_current_user
from config import settings as setting


class BaseModel(models.Model):
    user_creation = models.ForeignKey(setting.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='%(app_label)s_%(class)s_creation')
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    user_updated = models.ForeignKey(setting.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='%(app_label)s_%(class)s_updated')
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

"""MODELO BASE"""
class ModeloBase(models.Model):
    # CAMPOS POR DEFECTO PARA TODOS LOS MODELOS
    usu_insercion = models.ForeignKey(
        setting.AUTH_USER_MODEL,
        db_column="usu_insercion",
        verbose_name="Creado por",
        on_delete=models.RESTRICT,
        # related_name="+",
        related_name="%(app_label)s_%(class)s_inserciones",  # Cambiado related_name
        to_field="cod_usuario",  # Agregado to_field
        default="ACOR"  # Agregado default
    )
    fec_insercion = models.DateTimeField(
        verbose_name="Fecha Creación", auto_now_add=True
    )
    usu_modificacion = models.ForeignKey(
        setting.AUTH_USER_MODEL,
        db_column="usu_modificacion",
        verbose_name="Modificado por",
        on_delete=models.RESTRICT,
        # related_name="+",
        related_name="%(app_label)s_%(class)s_modificaciones",  # Cambiado related_name
        to_field="cod_usuario",  # Agregado to_field
        default="ACOR"  # Agregado default
    )
    fec_modificacion = models.DateTimeField(
        verbose_name="Fecha Modificación", auto_now=True
    )
    activo = models.BooleanField(default=True)
    
    def get_name_usu_insercion(self):
        return self.usu_insercion.first_name

    get_name_usu_insercion.short_description = "Creado por"

    def get_name_usu_modificacion(self):
        return self.usu_modificacion.first_name

    get_name_usu_modificacion.short_description = "Modificado por"

    """SAVE"""

    def save(self, *args, **kwargs):
        user = get_current_user()
        print(user)
        if user and not user.pk:
            user = None
        # print(dir(self))
        if not self.usu_insercion_id:
            self.usu_insercion = user
        self.usu_modificacion = user
        super(ModeloBase, self).save(*args, **kwargs)

    class Meta:
        abstract = True