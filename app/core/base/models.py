import os


from core.models import ModeloBase
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import model_to_dict
from config import settings as setting

from core.base.choices import *
from core.base.utils import calculate_age


# Create your models here.
"""REFERENCIA CABECERA"""
class RefCab(ModeloBase):
    cod = models.CharField(
        verbose_name="Codigo", db_column="cod", max_length=20, unique=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "bs_refcab"
        verbose_name = "Referencia Cabecera"
        verbose_name_plural = "Referencias Cabecera"


"""REFERENCIA DETALLE"""
class RefDet(ModeloBase):
    refcab = models.ForeignKey(
        RefCab,
        verbose_name="Referencia Cabecera",
        on_delete=models.RESTRICT,
        related_name="referencia",
    )
    cod = models.CharField(
        verbose_name="Codigo", db_column="cod", max_length=20, unique=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)

    def __str__(self):
        return self.denominacion or ""

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "bs_refdet"
        verbose_name = "Referencia Detalle"
        verbose_name_plural = "Referencias Detalle"
        unique_together = ["refcab", "cod"]


"""MESES"""
class Meses(ModeloBase):
    # id = models.CharField('Código',db_column='cod_modulo',max_length=2,primary_key=True)
    mes = models.IntegerField("Mes", db_column="mes", primary_key=True)
    denominacion = models.CharField(max_length=20, unique=True)
    cant_dias = models.IntegerField()

    def __str__(self):
        return f"{self.mes} - {self.denominacion}"

    class Meta:
        # ordering = ['id', ]
        db_table = "bs_meses"
        verbose_name = "meses"
        verbose_name_plural = "meses"


"""MODULOS"""
class Modulo(ModeloBase):
    cod_modulo = models.CharField(
        "Código", db_column="cod_modulo", max_length=2, primary_key=True
    )
    denominacion = models.CharField(max_length=100, unique=True)
    tipo_cartera = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 12},
        db_column="tipo_cartera",
        on_delete=models.RESTRICT,
        related_name="modulo_tipo_cartera",
        max_length=1,
        default="N",
    )

    def __str__(self):
        return f"{self.cod_modulo} - {self.denominacion}"

    class Meta:
        # ordering = ['id', ]
        db_table = "bs_modulo"
        verbose_name = "modulo"
        verbose_name_plural = "modulos"


"""TRANSACION"""
class Transaccion(ModeloBase):
    cod_transaccion = models.IntegerField(verbose_name="Código", primary_key=True)
    modulo = models.ForeignKey(
        Modulo,
        db_column="cod_modulo",
        verbose_name="Modulo",
        on_delete=models.RESTRICT,
        related_name="transacciones",
    )
    denominacion = models.CharField(
        verbose_name="Transaccion", max_length=100, unique=True
    )
    tipo_dc = models.CharField(
        verbose_name="Tipo", max_length=1, choices=choiceTipoDC()
    )
    tipo_acceso = models.CharField(
        verbose_name="Tipo Acceso", max_length=1, choices=choiceTipoAcceso()
    )
    abreviatura = models.CharField(verbose_name="Abreviatura", max_length=15)
    imprime_comprobante = models.BooleanField(
        verbose_name="Imprime Comprobante", null=True, blank=True, default=False
    )
    transaccion_por_defecto = models.BooleanField(
        verbose_name="Transacción Por Defecto", null=True, blank=True, default=False
    )
    url = models.CharField(
        max_length=100, verbose_name="Url", unique=True, null=True, blank=True
    )

    # Si la transaccion es por defecto, automaticamente es la opcion disponible para los movimientos, si no se elige otra opcion
    def __str__(self):
        return f"{self.cod_transaccion}-{self.denominacion}"

    class Meta:
        ordering = [
            "cod_transaccion",
        ]
        db_table = "bs_transaccion"
        verbose_name = "Transaccion"
        verbose_name_plural = "Transacciones"


"""PARAMETROS GENERALES"""
class Parametro(ModeloBase):
    modulo = models.ForeignKey(
        Modulo, verbose_name="Modulo", on_delete=models.RESTRICT, related_name="modulos"
    )
    parametro = models.CharField(max_length=25, unique=True)
    descripcion = models.CharField(max_length=100, unique=True)
    valor = models.CharField(max_length=100)

    def __str__(self):
        return "%s - %s " % (self.parametro, self.valor)

    class Meta:
        ordering = [
            "parametro",
        ]
        db_table = "bs_parametro"
        verbose_name = "Parametro"
        verbose_name_plural = "Parametros"


# PAISES
class Pais(ModeloBase):
    # ID
    cod = models.CharField(verbose_name="Código", max_length=3, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )
    nacionalidad = models.CharField(
        verbose_name="Nacionalidad", max_length=100, unique=True, null=True, blank=True
    )

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_pais"
        verbose_name = "Pais"
        verbose_name_plural = "Paises"

# DEPARTAMENTO
class Departamento(ModeloBase):
    # ID
    pais = models.ForeignKey(
        Pais, verbose_name="Pais", on_delete=models.RESTRICT, related_name="paises"
    )
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_departamento"
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        unique_together = ["pais", "denominacion"]

# CIUDAD
class Ciudad(ModeloBase):
    # ID
    departamento = models.ForeignKey(
        Departamento,
        verbose_name="Departamento",
        on_delete=models.RESTRICT,
        related_name="departamento",
    )
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_ciudad"
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        # unique_together = ["departamento", "denominacion"]


# BARRIO
class Barrio(ModeloBase):
    # ID
    ciudad = models.ForeignKey(
        Ciudad,
        verbose_name="Ciudad",
        on_delete=models.RESTRICT,
        related_name="ciudades",
    )
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    def toJSON(self):
        return model_to_dict(self)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_barrio"
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"
        unique_together = ["ciudad", "denominacion"]


# EMPRESA
class Empresa(ModeloBase):
    ruc = models.CharField(
        verbose_name="RUC", max_length=10, validators=[MinLengthValidator(6)]
    )
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )
    nombre_fantasia = models.CharField(
        verbose_name="Nombre de Fantasía", max_length=100, unique=True
    )
    direccion = models.CharField(verbose_name="Dirección", max_length=100)
    telefono = models.CharField(verbose_name="Teléfono", max_length=20)
    celular = models.CharField(
        verbose_name="Celular", max_length=20, null=True, blank=True
    )
    email = models.CharField(max_length=50, verbose_name="Email", null=True, blank=True)
    website = models.CharField(
        max_length=250, verbose_name="Página web", null=True, blank=True
    )
    descripcion = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Descripción"
    )
    imagen = models.ImageField(
        null=True, blank=True, upload_to="empresa/%Y/%m/%d", verbose_name="Logo"
    )
    iva = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=9, verbose_name="Iva"
    )

    def __str__(self):
        return self.denominacion

    def getNombreFantasia(self):
        return self.nombre_fantasia

    def get_image(self):
        if self.imagen:
            return "{}{}".format(setting.MEDIA_URL, self.imagen)
        return "{}{}".format(setting.STATIC_URL, "img/default/empty.png")

    def get_iva(self):
        return format(self.iva, ".2f")

    def remove_image(self):
        try:
            if self.imagen:
                os.remove(self.imagen.path)
        except:
            pass
        finally:
            self.imagen = None

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        # ordering = ['1',]
        db_table = "bs_empresa"
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        default_permissions = ()
        permissions = (("view_empresa", "Can view Empresa"),)
        ordering = ["-id"]


"""SUCURSAL"""
class Sucursal(ModeloBase):
    # ID
    empresa = models.ForeignKey(
        Empresa,
        verbose_name="Empresa",
        on_delete=models.RESTRICT,
        related_name="empresa",
    )
    cod = models.CharField(verbose_name="Código", max_length=3)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )
    denominacion_corta = models.CharField(
        verbose_name="Denominación Corta",
        max_length=25,
        unique=True,
        null=True,
        blank=True,
    )
    denominacion_puesto = models.CharField(
        verbose_name="Denominación de Puesto",
        max_length=35,
        unique=True,
        null=True,
        blank=True,
    )
    direccion = models.CharField(verbose_name="Dirección", max_length=100)
    telefono = models.CharField(verbose_name="Teléfono", max_length=100)

    def __str__(self):
        return "{}".format(self.denominacion)

    def get_short_name(self):
        return "{}".format(self.denominacion_corta)

    class Meta:
        # ordering = ['1',]
        db_table = "bs_sucursal"
        verbose_name = "sucursal"
        verbose_name_plural = "sucursales"


# MONEDA
class Moneda(ModeloBase):
    # ID
    cod_moneda = models.CharField(verbose_name="Código", max_length=3, unique=True)
    iso = models.CharField(verbose_name="ISO", max_length=3, unique=True)
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)
    decimales = models.IntegerField(verbose_name="Decimales")
    fec_cotizacion = models.DateField(verbose_name="Fecha Cotizacion")
    precio_compra = models.FloatField(verbose_name="Precio Compra")
    precio_venta = models.FloatField(verbose_name="Precio Venta")

    def __str__(self):
        return "{}".format(self.denominacion)

    class Meta:
        # ordering = ['1',]
        db_table = "bs_moneda"
        verbose_name = "moneda"
        verbose_name_plural = "monedas"

# PERSONA
class Persona(ModeloBase):
    ci = models.BigIntegerField(verbose_name="CI", unique=True)
    ruc = models.CharField(
        verbose_name="RUC",
        max_length=10,
        validators=[MinLengthValidator(6)],
        unique=True,
        null=True,
        blank=True,
    )
    nombre = models.CharField(verbose_name="Nombre", max_length=150)
    apellido = models.CharField(verbose_name="Apellido", max_length=150)
    nacionalidad = models.ForeignKey(
        Pais, verbose_name="Nacionalidad", on_delete=models.RESTRICT
    )
    ciudad = models.ForeignKey(
        Ciudad, verbose_name="Ciudad", on_delete=models.RESTRICT, null=True, blank=True
    )
    barrio = models.ForeignKey(
        Barrio, verbose_name="Barrio", on_delete=models.RESTRICT, null=True, blank=True
    )
    direccion = models.CharField(
        verbose_name="Dirección", max_length=100, null=True, blank=True
    )
    telefono = models.CharField(
        verbose_name="Teléfono", max_length=20, null=True, blank=True
    )
    celular = models.CharField(
        verbose_name="Celular", max_length=20, null=True, blank=True
    )
    email = models.CharField(max_length=50, verbose_name="Email", null=True, blank=True)
    fec_nacimiento = models.DateField(verbose_name="Fecha Nacimiento", null=True)
    sexo = models.ForeignKey(
        RefDet,
        to_field="cod",
        verbose_name="Genero",
        db_column="sexo",
        on_delete=models.RESTRICT,
        related_name="sexo",
        max_length=1,
        blank=True,
        null=True,
    )
    estado_civil = models.ForeignKey(
        RefDet,
        to_field="cod",
        verbose_name="Estado Civil",
        db_column="estado_civil",
        on_delete=models.RESTRICT,
        related_name="estado_civil",
        max_length=2,
        blank=True,
        null=True,
    )

    def get_full_name(self):
        return "{}, {}".format(self.nombre, self.apellido)

    def __str__(self):
        return "{}, {}".format(self.nombre, self.apellido)

    def get_edad(self):
        return calculate_age(self.fec_nacimiento)

    def toJSON(self):
        item = model_to_dict(self)
        item["edad"] = self.get_edad()
        return item

    class Meta:
        db_table = "bs_persona"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"

