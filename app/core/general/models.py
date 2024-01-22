from django.db import models
from django.forms import model_to_dict

from core.base.models import (
    ModeloBase,
    Modulo,
    Moneda,
    Persona,
    RefDet,
    Sucursal,
    Transaccion,
)


# CALIFICACION CLIENTE
class CalificacionCliente(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=1, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )
    promedio_atraso = models.IntegerField(verbose_name="Promedio Atraso")

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "ge_calificacion_cliente"
        verbose_name = "Calificacion Cliente"
        verbose_name_plural = "Calificacion Clientes"


# ESTADO CLIENTE
class EstadoCliente(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=4, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "ge_estado_cliente"
        verbose_name = "Estado Cliente"
        verbose_name_plural = "Estado Clientes"


# SOCIO
class Cliente(ModeloBase):
    cod_cliente = models.IntegerField(verbose_name="Cod. Cliente", primary_key=True)
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="cliente_sucursal",
    )
    nro_socio = models.IntegerField(verbose_name="Nro. Socio", unique=True)
    persona = models.ForeignKey(
        Persona,
        verbose_name="Persona",
        on_delete=models.RESTRICT,
        related_name="cliente_persona",
    )
    fec_ingreso = models.DateField(verbose_name="Fecha Ingreso")
    fec_retiro = models.DateField(verbose_name="Fecha Retiro", null=True, blank=True)
    estado = models.ForeignKey(
        EstadoCliente,
        to_field="cod",
        db_column="estado",
        verbose_name="Estado Cliente",
        on_delete=models.RESTRICT,
        related_name="cliente_estado",
    )
    calificacion = models.ForeignKey(
        CalificacionCliente,
        to_field="cod",
        db_column="calificacion",
        verbose_name="Calificacion Cliente",
        on_delete=models.RESTRICT,
        related_name="cliente_calificacion",
    )
    comentario = models.CharField(
        verbose_name="Comentario", max_length=100, null=True, blank=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_socio, self.persona)

    def get_nro_socio_nombre(self):
        return "{} - {}".format(self.nro_socio, self.persona)

    def toJSON(self):
        item = model_to_dict(self)
        item["persona"] = str(self.persona)
        item["ci"] = self.persona.ci
        item["telefono"] = (
            self.persona.telefono if self.persona.telefono else self.persona.celular
        )
        item["fec_ingreso"] = (
            self.fec_ingreso.strftime("%d/%m/%Y") if self.fec_ingreso else None
        )
        item["fec_retiro"] = (
            self.fec_retiro.strftime("%d/%m/%Y") if self.fec_retiro else None
        )
        return item

    class Meta:
        db_table = "ge_cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


# TIPO MOVIMIENTO
class TipoMovimiento(ModeloBase):
    tip_movimiento = models.CharField(
        verbose_name="Código", max_length=1, primary_key=True
    )
    denominacion = models.CharField(
        verbose_name="Tipo Movimiento", max_length=100, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.tip_movimiento, self.denominacion)

    class Meta:
        ordering = [
            "tip_movimiento",
        ]
        db_table = "ge_tipo_movimiento"
        verbose_name = "Tipo Movimiento"
        verbose_name_plural = "Tipos Movimientos"


"""MOVIMIENTO GENERAL BASE ABSTRACT"""


class MovimientoBase(ModeloBase):
    fec_movimiento = models.DateField(verbose_name="Fecha Movimiento")
    cod_movimiento = models.CharField(verbose_name="Codigo Movimiento", max_length=8)
    tip_movimiento = models.ForeignKey(
        TipoMovimiento,
        verbose_name="Tipo",
        db_column="tip_movimiento",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_tip_movimiento",
    )
    modulo = models.ForeignKey(
        Modulo,
        verbose_name="Modulo",
        db_column="cod_modulo",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_modulo",
    )
    transaccion = models.ForeignKey(
        Transaccion,
        verbose_name="Transacción",
        db_column="cod_transaccion",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_transaccion",
    )

    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_sucursal",
    )
    cliente = models.ForeignKey(
        Cliente,
        db_column="cod_cliente",
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_cliente",
    )
    moneda = models.ForeignKey(
        Moneda,
        verbose_name="Moneda",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_moneda",
    )
    cuenta_operativa = models.CharField(
        verbose_name="Cuenta Operativa", max_length=50, null=True, blank=True
    )
    concepto = models.CharField(verbose_name="Concepto", max_length=100, blank=True)
    importe = models.DecimalField(
        verbose_name="Importe", default=0, max_digits=20, decimal_places=2
    )
    monto_pagado = models.DecimalField(
        verbose_name="Monto Pagado", default=0, max_digits=20, decimal_places=2
    )
    nombre_campo = models.CharField(
        verbose_name="Nombre Campo", max_length=100, null=True, blank=True, default=None
    )
    referencia = models.CharField(
        verbose_name="Referencia", max_length=100, null=True, blank=True, default=None
    )

    nro_documento = models.CharField(
        verbose_name="Nro. Documento", max_length=25, null=True, blank=True
    )
    vigencia_desde = models.DateField(
        verbose_name="Vigencia Desde", blank=True, null=True, default=None
    )
    vigencia_hasta = models.DateField(
        verbose_name="Vigencia Hasta", blank=True, null=True, default=None
    )
    fec_movimiento_pago = models.DateField(
        verbose_name="Fecha Movimiento Pago", null=True, blank=True
    )
    cod_movimiento_pago = models.CharField(
        verbose_name="Codigo Movimiento Pago", max_length=8, null=True, blank=True
    )

    class Meta:
        abstract = True


"""MOVIMIENTOS GENERALES NO CONTABLES"""
"""MOVIMIENTOS DIARIOS"""


class Movimiento(MovimientoBase):
    def toJSON(self):
        item = model_to_dict(self)
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["importe"] = format(self.importe, ".2f")
        item["monto_pagado"] = format(self.monto_pagado, ".2f")
        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "ge_movimientos"
        verbose_name = "Movimiento Diario"
        verbose_name_plural = "Movimientos Diarios"


"""MOVIMIENTOS MENSUALES DEL PERIODO ACTUAL"""


class MovimientosMensuales(MovimientoBase):
    def toJSON(self):
        item = model_to_dict(self)
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["importe"] = format(self.importe, ".2f")
        item["monto_pagado"] = format(self.monto_pagado, ".2f")
        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "ge_movimientos_mensuales"
        verbose_name = "Movimientos Mensuales"
        verbose_name_plural = "Movimientos Mensuales"


"""MOVIMIENTOS ANUALES HASTA PERIOD ANTERIOR"""


class MovimientosAnuales(MovimientoBase):
    def toJSON(self):
        item = model_to_dict(self)
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["importe"] = format(self.importe, ".2f")
        item["monto_pagado"] = format(self.monto_pagado, ".2f")
        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "ge_movimientos_anuales"
        verbose_name = "Movimientos Anuales"
        verbose_name_plural = "Movimientos Anuales"


"""PLAZOS EN DIAS"""


class Plazo(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    plazo = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 5},
        db_column="plazo",
        on_delete=models.RESTRICT,
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
        db_table = "ge_plazo"
        verbose_name = "Plazos en Dias"
        verbose_name_plural = "Plazos en Dias"
