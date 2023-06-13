from datetime import datetime

from django.db import models
from django.db.models import Q
from django.forms import model_to_dict

from core.base.choices import choiceMultipleDesembolso, choiceSiNo
from core.base.models import ModeloBase, Moneda, RefDet, Sucursal
from core.contable.models import PlanDeCuenta
from core.socio.models import Socio

# Create your models here.
"""SITUACION PRESTAMO"""
# *Segun el nivel define la aprobacion


class NivelAprobacion(ModeloBase):
    cod_nivel_aprobacion = models.CharField(
        verbose_name="Cod. Nivel Aprobacion",
        db_column="cod_nivel_aprobacion",
        max_length=4,
        unique=True,
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)

    def __str__(self):
        return f"{self.denominacion} - {self.cod_nivel_aprobacion}"

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "pr_nivel_aprobacion"
        verbose_name = "Nivel Aprobacion"
        verbose_name_plural = "Nivel Aprobacion"


class SituacionPrestamo(ModeloBase):
    cod = models.CharField(
        verbose_name="Codigo", db_column="cod", max_length=4, unique=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    rango_inferior = models.IntegerField(default=0)
    rango_superior = models.IntegerField(default=0)

    def __str__(self):
        return "{} - {} de {} a {}".format(
            self.cod, self.denominacion, self.rango_inferior, self.rango_superior
        )

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "pr_situacion_prestamo"
        verbose_name = "Situacion Prestamo"
        verbose_name_plural = "Situacion Prestamo"


"""ESQUEMA CONTABLE PRESTAMO"""


class EsquemaContable(ModeloBase):
    plazo = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 5},
        db_column="plazo",
        on_delete=models.RESTRICT,
        related_name="plazo",
        max_length=1,
    )
    vencimiento = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 6},
        db_column="vencimiento",
        on_delete=models.RESTRICT,
        related_name="vencimiento",
        max_length=1,
    )
    estado_socio = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 3},
        db_column="estado_socio",
        on_delete=models.RESTRICT,
        related_name="estado_socio",
        max_length=4,
    )
    situacion_prestamo = models.ForeignKey(
        SituacionPrestamo,
        to_field="cod",
        default="NORM",
        db_column="situacion_prestamo",
        on_delete=models.RESTRICT,
        related_name="situacion_prestamo",
        max_length=4,
    )
    rubro_comision = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_comision",
        on_delete=models.PROTECT,
        related_name="rubro_comision",
    )
    rubro_capital = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_capital",
        on_delete=models.PROTECT,
        related_name="rubro_capital",
    )
    rubro_interes = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_interes",
        on_delete=models.PROTECT,
        related_name="rubro_intres",
    )
    rubro_interes_moratorio = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_interes_moratorio",
        on_delete=models.PROTECT,
        related_name="rubro_interes_moratorio",
    )
    rubro_interes_punitorio = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_interes_punitorio",
        on_delete=models.PROTECT,
        related_name="rubro_interes_punitorio",
    )
    rubro_capital_inverso = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_capital_inverso",
        on_delete=models.PROTECT,
        related_name="rubro_capital_inverso",
    )
    rubro_desafectacion = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_desafectacion",
        on_delete=models.PROTECT,
        related_name="rubro_desafectacion",
    )
    rubro_constitucion = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_constitucion",
        on_delete=models.PROTECT,
        related_name="rubro_constitucion",
    )
    rubro_prevision = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_prevision",
        on_delete=models.PROTECT,
        related_name="rubro_prevision",
    )
    vinculado = models.CharField(max_length=1, default="N", choices=choiceSiNo())

    def __str__(self):
        return f"{str(self.plazo)}->{str(self.vencimiento)}-> SOCIO: {str(self.estado_socio)}->\
                 {str(self.situacion_prestamo)}-> VINCULADO: {str(self.vinculado)}"

    class Meta:
        db_table = "pr_esquema_contable"
        verbose_name = "Esquema Contable "
        verbose_name_plural = "Esquemas Contables"


"""TIPO PRESTAMO"""


class TipoPrestamo(ModeloBase):
    denominacion = models.CharField(max_length=100)
    denom_corta = models.CharField(verbose_name="Denominacion Corta", max_length=8)
    cod_grupo_prestamo = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 7},
        db_column="cod_grupo_prestamo",
        on_delete=models.RESTRICT,
        related_name="grupo_prestamo",
        max_length=4,
        null=True,
    )
    cod_nivel_aprobacion = models.ForeignKey(
        NivelAprobacion,
        to_field="cod_nivel_aprobacion",
        db_column="cod_nivel_aprobacion",
        on_delete=models.RESTRICT,
        related_name="nivel_aprobacion",
        max_length=4,
        null=True,
    )
    cod_forma_desembolso = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 10},
        db_column="cod_forma_desembolso",
        on_delete=models.RESTRICT,
        related_name="forma_desembolso",
        max_length=4,
        default="EFEC",
    )
    multiple_desembolso = models.IntegerField(
        default=1, choices=choiceMultipleDesembolso()
    )
    tasa_interes_moratorio = models.DecimalField(
        default=0, max_digits=4, decimal_places=2
    )
    tasa_interes_punitorio = models.DecimalField(
        default=0, max_digits=4, decimal_places=2
    )
    requiere_liquidacion = models.BooleanField(default=True)

    def __str__(self):
        return f"{str(self.denominacion)} -> {str(self.cod_grupo_prestamo)}"

    class Meta:
        db_table = "pr_tipo_prestamo"
        verbose_name = "Tipo Prestamo"
        verbose_name_plural = "Tipos Prestamos"


"""SITUACION SOLICITUD"""


class SituacionSolicitud(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)
    situacion_final = models.CharField(
        verbose_name="Situacion Final", max_length=1, choices=choiceSiNo(), default="N"
    )
    # Estado Solicitud: Para aplicar segun situacion de la Solicitud de Prestamo
    estado = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 4},
        db_column="estado",
        on_delete=models.RESTRICT,
        related_name="estado_solicitud2",
        max_length=1,
    )
    cod_nivel_aprobacion = models.ForeignKey(
        NivelAprobacion,
        to_field="cod_nivel_aprobacion",
        db_column="cod_nivel_aprobacion",
        on_delete=models.RESTRICT,
        related_name="nivel_aprobacion_situacion",
        max_length=4,
        null=True,
    )

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_situacion_solicitud"
        verbose_name = "Situacion Solicitud"
        verbose_name_plural = "Situacion Solicitud"


"""CLASIFICACION POR DESTINO """


class ClasificacionPorDestino(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_clasificacion_por_destino"
        verbose_name = "Clasificacion por Destino de Prestamo"
        verbose_name_plural = "Clasificacion por Destino de Prestamos"


"""DESTINO PRESTAMO"""


class DestinoPrestamo(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)
    grupo_prestamo = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 7},
        db_column="grupo_prestamo",
        on_delete=models.RESTRICT,
        related_name="grupo_prestamo2",
        max_length=4,
    )
    clasificacion_por_destino = models.ForeignKey(
        ClasificacionPorDestino,
        on_delete=models.PROTECT,
        related_name="clasificacion_por_destino",
    )

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_destino_prestamo"
        verbose_name = "Destino de Prestamos"
        verbose_name_plural = "Destinos de Prestamos"


"""SOLICITUD DE PRESTAMO"""


class SolicitudPrestamo(ModeloBase):
    nro_solicitud = models.CharField(
        verbose_name="Nro. Solicitud",
        db_column="nro_solicitud",
        max_length=10,
        unique=True,
    )
    nro_prestamo = models.CharField(
        verbose_name="Nro. Prestamo",
        db_column="nro_prestamo",
        max_length=10,
        unique=True,
        null=True,
        blank=True,
    )
    fec_solicitud = models.DateField(verbose_name="Fecha Solicitud")
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.PROTECT
    )
    socio = models.ForeignKey(Socio, verbose_name="Socio", on_delete=models.PROTECT)
    tipo_prestamo = models.ForeignKey(
        TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
    )
    destino_prestamo = models.ForeignKey(
        DestinoPrestamo, verbose_name="Destino Prestamo", on_delete=models.PROTECT
    )
    monto_solicitado = models.DecimalField(
        verbose_name="Monto Solicitado", max_digits=14, decimal_places=2, default=0
    )
    monto_prestamo = models.DecimalField(
        verbose_name="Monto Prestamo", max_digits=14, decimal_places=2, default=0
    )
    monto_aprobado = models.DecimalField(
        verbose_name="Monto Aprobado", max_digits=14, decimal_places=2, default=0
    )
    monto_refinanciado = models.DecimalField(
        verbose_name="Monto Refinanciado", max_digits=14, decimal_places=2, default=0
    )
    monto_neto = models.DecimalField(
        verbose_name="Monto Neto", max_digits=14, decimal_places=2, default=0
    )
    monto_cuota_inicial = models.DecimalField(
        verbose_name="Monto Cuota Inicial", max_digits=14, decimal_places=2, default=0
    )
    plazo_mes = models.IntegerField()
    moneda = models.ForeignKey(Moneda, verbose_name="Moneda", on_delete=models.PROTECT)
    estado = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 4},
        db_column="estado",
        on_delete=models.RESTRICT,
        related_name="estado_solicitud",
        max_length=1,
    )
    tasa_interes = models.DecimalField(
        verbose_name="Tasa Interes", default=0, max_digits=4, decimal_places=2
    )
    cant_cuota = models.IntegerField()  # Cantidad Cuota por Año
    cant_desembolso = models.IntegerField(default=0, null=True)
    fec_desembolso = models.DateField(
        verbose_name="Fecha Desembolso", blank=True, null=True
    )
    fec_primer_vto = models.DateField(
        verbose_name="Fecha Primer Vencimiento", blank=True, null=True
    )
    total_interes = models.DecimalField(
        verbose_name="Total Interes", max_digits=14, decimal_places=2, default=0
    )
    liquidado = models.CharField(
        verbose_name="Liquidado", max_length=1, choices=choiceSiNo(), default="N"
    )
    nro_acta = models.CharField(
        verbose_name="Nro. Acta", max_length=20, blank=True, null=True
    )
    fec_acta = models.DateField(verbose_name="Fecha Acta", blank=True, null=True)
    nro_resolucion = models.CharField(
        verbose_name="Nro. Resolucion", max_length=20, blank=True, null=True
    )
    cod_forma_desembolso = models.ForeignKey(
        RefDet,
        to_field="cod",
        limit_choices_to={"refcab_id": 10},
        db_column="cod_forma_desembolso",
        on_delete=models.RESTRICT,
        related_name="forma_desembolso_solicitud",
        max_length=4,
        default="EFEC",
    )
    situacion_solicitud = models.ForeignKey(
        SituacionSolicitud, verbose_name="Situacion Solicitud", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.nro_solicitud} - {self.socio}"

    def toJSON(self):
        # item = model_to_dict(self)
        item = {}
        item["nro_solicitud"] = str(self.nro_solicitud)
        item["socio"] = str(self.socio.persona)
        item["telefono"] = self.socio.persona.telefono
        item["fec_solicitud"] = (
            self.fec_solicitud.strftime("%d/%m/%Y") if self.fec_solicitud else None
        )
        # La fecha de acta indica la APROBACION O DESAPROBACION DEL CREDITO OP 503
        item["fec_acta"] = self.fec_acta.strftime("%d/%m/%Y") if self.fec_acta else None
        item["estado"] = self.estado.denominacion
        return item

    class Meta:
        db_table = "pr_solicitud_prestamo"
        verbose_name = "Solicitud de Prestamo"
        verbose_name_plural = "Solicitudes de Prestamos"


"""PROFORMA CUOTAS DE PRESTAMO"""


# *SE GENERA CON LA SOLICITUD DE PRESTAMO
# *APROBADO LA SOLICITUD SE INSERTA EN LA TABLA PR_CUOTAS_PRESTAMO
class ProformaCuotaPrestamo(ModeloBase):
    solicitud = models.ForeignKey(
        SolicitudPrestamo,
        db_column="nro_solicitud",
        verbose_name="Nro. Solicitud",
        on_delete=models.RESTRICT,
        related_name="solicitud",
        blank=True,
        null=True,
    )
    nro_cuota = models.IntegerField()
    fec_vencimiento = models.DateField(verbose_name="Fecha Vencimiento")
    saldo_anterior_capital = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    amortizacion = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    aporte_extraordinario = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    comision = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    seguro_vida = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tasa_interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "pr_proforma_cuota_prestamo"
        verbose_name = "Proforma Cuota Prestamo"
        verbose_name_plural = "Proforma Cuota Prestamo"


# TODO: FALTA TERMINAR DEFINIR PRIMERO EL MODELO PRESTAMO
# class PrestamoRefinanciado(ModeloBase):
#     nro_prestamo = models.ForeignKey(
#         TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
#     )
#     tipo_prestamo = models.ForeignKey(
#         TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
#     )
#     nro_solicitud = models.CharField(
#         verbose_name="Nro. Solicitud",
#         db_column="nro_solicitud",
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )
#     fec_solicitud = models.DateField(verbose_name="Fecha Solicitud")
#     sucursal = models.ForeignKey(
#         Sucursal, verbose_name="Sucursal", on_delete=models.PROTECT
#     )
#     socio = models.ForeignKey(Socio, verbose_name="Socio", on_delete=models.PROTECT)
#     tipo_prestamo = models.ForeignKey(
#         TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
#     )
#     destino_prestamo = models.ForeignKey(
#         DestinoPrestamo, verbose_name="Destino Prestamo", on_delete=models.PROTECT
#     )
#     monto_solicitado = models.DecimalField(
#         verbose_name="Monto Solicitado", max_digits=14, decimal_places=2, default=0
#     )
#     monto_prestamo = models.DecimalField(
#         verbose_name="Monto Prestamo", max_digits=14, decimal_places=2, default=0
#     )
#     monto_aprobado = models.DecimalField(
#         verbose_name="Monto Aprobado", max_digits=14, decimal_places=2, default=0
#     )
#     monto_refinanciado = models.DecimalField(
#         verbose_name="Monto Refinanciado", max_digits=14, decimal_places=2, default=0
#     )
#     monto_neto = models.DecimalField(
#         verbose_name="Monto Neto", max_digits=14, decimal_places=2, default=0
#     )
#     monto_cuota_inicial = models.DecimalField(
#         verbose_name="Monto Cuota Inicial", max_digits=14, decimal_places=2, default=0
#     )
#     plazo_mes = models.IntegerField()
#     moneda = models.ForeignKey(Moneda, verbose_name="Moneda", on_delete=models.PROTECT)
#     estado = models.ForeignKey(
#         RefDet,
#         to_field="cod",
#         limit_choices_to={"refcab_id": 4},
#         db_column="estado",
#         on_delete=models.RESTRICT,
#         related_name="estado_solicitud",
#         max_length=1,
#     )
#     tasa_interes = models.DecimalField(
#         verbose_name="Tasa Interes", default=0, max_digits=4, decimal_places=2
#     )
#     cant_cuota = models.IntegerField()  # Cantidad Cuota por Año
#     cant_desembolso = models.IntegerField(default=0, null=True)
#     fec_desembolso = models.DateField(
#         verbose_name="Fecha Desembolso", blank=True, null=True
#     )
#     fec_primer_vto = models.DateField(
#         verbose_name="Fecha Primer Vencimiento", blank=True, null=True
#     )
#     total_interes = models.DecimalField(
#         verbose_name="Total Interes", max_digits=14, decimal_places=2, default=0
#     )
#     liquidado = models.CharField(
#         verbose_name="Liquidado", max_length=1, choices=choiceSiNo(), default="N"
#     )
#     nro_acta = models.CharField(
#         verbose_name="Nro. Acta", max_length=20, blank=True, null=True
#     )
#     fec_acta = models.DateField(verbose_name="Fecha Acta", blank=True, null=True)
#     cod_forma_desembolso = models.ForeignKey(
#         RefDet,
#         to_field="cod",
#         limit_choices_to={"refcab_id": 10},
#         db_column="cod_forma_desembolso",
#         on_delete=models.RESTRICT,
#         related_name="forma_desembolso_solicitud",
#         max_length=4,
#         default="EFEC",
#     )
#     situacion_solicitud = models.ForeignKey(
#         SituacionSolicitud, verbose_name="Situacion Solicitud", on_delete=models.PROTECT
#     )

#     def __str__(self):
#         return f"{self.nro_solicitud} - {self.socio}"

#     class Meta:
#         db_table = "pr_solicitud_prestamo"
#         verbose_name = "Solicitud de Prestamo"
#         verbose_name_plural = "Solicitudes de Prestamos"
