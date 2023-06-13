import os
from datetime import datetime

from crum import get_current_user
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import model_to_dict

from config import settings
from core.base.choices import *

# Create your models here.

"""MODELO BASE"""


class ModeloBase(models.Model):
    # RefDets = RefDet.objects.filter(cod_referencia='ESTADO')
    # CAMPOS POR DEFECTO PARA TODOS LOS MODELOS
    usu_insercion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="usu_insercion",
        verbose_name="Creado por",
        on_delete=models.RESTRICT,
        related_name="+",
    )
    fec_insercion = models.DateTimeField(
        verbose_name="Fecha Creación", auto_now_add=True
    )
    usu_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="usu_modificacion",
        verbose_name="Modificado por",
        on_delete=models.RESTRICT,
        related_name="+",
    )
    fec_modificacion = models.DateTimeField(
        verbose_name="Fecha Modificación", auto_now=True
    )
    activo = models.BooleanField(default=True)
    # estado = models.ForeignKey(RefDet,db_column='estado',on_delete=models.RESTRICT,limit_choices_to={'referencia': 'ESTADO'},to_field='valor',default='A')

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

    # def nacionalidad(self):
    # 	return self.nacionalidad

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_pais"
        verbose_name = "Pais"
        verbose_name_plural = "Paises"


# CIUDAD
class Ciudad(ModeloBase):
    # ID
    pais = models.ForeignKey(
        Pais, verbose_name="Pais", on_delete=models.RESTRICT, related_name="paises"
    )
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_ciudad"
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        unique_together = ["pais", "denominacion"]


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
    desc = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="Descripción"
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
            return "{}{}".format(settings.MEDIA_URL, self.imagen)
        return "{}{}".format(settings.STATIC_URL, "img/default/empty.png")

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


# TIPOS DE COMPROBANTES FACTURA, RECIBO,ETC
class TipoComprobante(ModeloBase):
    # ID
    tip_comprobante = models.CharField(
        verbose_name="Tipo Comprobante", max_length=6, unique=True
    )
    descripcion = models.CharField(verbose_name="Descripción", max_length=100)
    operacion_stock = models.CharField(
        verbose_name="Operacion Stock",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceOperacionSaldo(),
    )
    operacion_saldo = models.CharField(
        verbose_name="Operacion Saldo",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceOperacionSaldo(),
    )
    ver_en_recibo = models.CharField(
        verbose_name="Ver en Recibo",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceSiNo(),
    )
    ver_en_compra = models.CharField(
        verbose_name="Ver en Compra",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceSiNo(),
    )
    ver_en_venta = models.CharField(
        verbose_name="Ver en Venta",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceSiNo(),
    )
    nro_de_lineas = models.IntegerField(verbose_name="Nro. de Lineas Pre-Impreso")

    def __str__(self):
        return "{} - {}".format(self.tip_comprobante, self.descripcion)

    class Meta:
        # ordering = ['1',]
        db_table = "bs_tipo_comprobante"
        verbose_name = "Tipo de Comprobante"
        verbose_name_plural = "Tipos de Comprobantes"


# SECTOR OPERATIVO
class SectorOperativo(ModeloBase):
    # ID
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="fk_sucursal_%(app_label)s_%(class)s",
    )
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_sector_operativo"
        verbose_name = "Sector Operativo"
        verbose_name_plural = "Sectores Operativos"


# TIPO MOVIMIENTO
class Caja(ModeloBase):
    nro_caja = models.IntegerField(
        verbose_name="Nro. Caja", db_column="nro_caja", primary_key=True
    )
    denominacion = models.CharField(verbose_name="Caja", max_length=100, unique=True)
    impresora1 = models.CharField(
        verbose_name="Impresora 1", max_length=100, blank=True, null=True
    )
    impresora2 = models.CharField(
        verbose_name="Impresora 2", max_length=100, blank=True, null=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_caja, self.denominacion)

    class Meta:
        ordering = [
            "nro_caja",
        ]
        db_table = "bs_caja"
        verbose_name = "caja"
        verbose_name_plural = "cajas"


# TIPO MOVIMIENTO
class CajaComprobante(ModeloBase):
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.RESTRICT, null=True
    )
    nro_caja = models.ForeignKey(
        Caja, verbose_name="Nro. Caja", db_column="nro_caja", on_delete=models.RESTRICT
    )
    tip_comprobante = models.ForeignKey(
        TipoComprobante,
        verbose_name="Tipo Comprobante",
        db_column="tip_comprobante",
        to_field="tip_comprobante",
        on_delete=models.RESTRICT,
    )
    nro_timbrado = models.IntegerField(verbose_name="Nro. Timbrado")
    nro_ini_comprobante = models.BigIntegerField(
        verbose_name="Nro. Comprobante Inicial"
    )
    nro_fin_comprobante = models.BigIntegerField(verbose_name="Nro. Comprobante Final")
    nro_act_comprobante = models.BigIntegerField(verbose_name="Nro. Comprobante Actual")
    fec_vigencia_desde = models.DateField(
        verbose_name="Fecha Vigencia Desde", null=True
    )
    fec_vigencia_hasta = models.DateField(
        verbose_name="Fecha Vigencia Hasta", null=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_caja, self.tip_comprobante)

    class Meta:
        # ordering = ['nro_caja',]
        db_table = "bs_caja_comprobante"
        verbose_name = "Caja Comprobante"
        verbose_name_plural = "Caja Comprobantes"
        unique_together = ["sucursal", "nro_caja", "tip_comprobante", "nro_timbrado"]


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
        on_delete=models.RESTRICT,
        related_name="estado_civil",
        max_length=2,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{}, {}".format(self.nombre, self.apellido)

    class Meta:
        db_table = "bs_persona"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"


"""PLAZOS EN DIAS"""


class Plazo(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    plazo = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 5},
        db_column="plazo",
        on_delete=models.RESTRICT,
        related_name="plazo_dias",
        max_length=1,
    )
    rango_inferior = models.IntegerField(default=0)
    rango_superior = models.IntegerField(default=0)
    contrato_inferior = models.IntegerField(default=0)
    contrato_superior = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.denominacion} - {self.plazo} "

    class Meta:
        ordering = ["id"]
        db_table = "bs_plazo"
        verbose_name = "Plazos en Dias"
        verbose_name_plural = "Plazos en Dias"
