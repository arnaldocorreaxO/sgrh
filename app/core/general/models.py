from django.db import models
from django.forms import model_to_dict

from core.base.models import ModeloBase, Modulo, Moneda, Sucursal, Transaccion
from core.contable.models import PlanDeCuenta, TipoMovimiento
from core.socio.models import Socio


# MOVIMIENTO ABSTRACT
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
    socio = models.ForeignKey(
        Socio,
        verbose_name="Socio",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_socio",
    )
    moneda = models.ForeignKey(
        Moneda,
        verbose_name="Moneda",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_moneda",
    )

    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        verbose_name="Rubro Contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_rubro_contable",
        blank=True,
        null=True,
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
