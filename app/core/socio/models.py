from datetime import datetime

from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import model_to_dict

from core.base.models import ModeloBase, Persona, Sucursal


# PROMOCION INGRESO
class PromocionIngreso(ModeloBase):
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )
    fec_vigencia_desde = models.DateField(verbose_name="Fecha Vigencia Desde")
    fec_vigencia_hasta = models.DateField(verbose_name="Fecha Vigencia Hasta")
    # Monto Inicial para Ingreso de Socio se paga unica vez en el ingreso del socio
    mto_ini_aporte_ingreso = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Monto Inicial Aporte Ingreso",
    )
    # Monto Inicial de la cuota de aporte social
    mto_ini_aporte_social = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Monto Inicial Aporte Social",
    )
    # Monto Inicial de la cuota de solidaridad
    mto_ini_aporte_solidaridad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Monto Inicial Aporte Solidaridad",
    )
    mto_ini_gastos_administrativos = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Monto Inicial Gastos Administrativos",
    )

    def toJSON(self):
        item = model_to_dict(self)
        item["fec_vigencia_desde"] = self.fec_vigencia_desde.strftime("%d/%m/%Y")
        item["fec_vigencia_hasta"] = self.fec_vigencia_hasta.strftime("%d/%m/%Y")
        item["mto_ini_aporte_ingreso"] = format(self.mto_ini_aporte_ingreso, ".0f")
        item["mto_ini_aporte_social"] = format(self.mto_ini_aporte_social, ".0f")
        item["mto_ini_aporte_solidaridad"] = format(
            self.mto_ini_aporte_solidaridad, ".0f"
        )
        item["mto_ini_gastos_administrativos"] = format(
            self.mto_ini_gastos_administrativos, ".0f"
        )

        return item

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "sc_promocion_ingreso"
        verbose_name = "Promocion Ingreso"
        verbose_name_plural = "Promociones Ingreso"


# CALIFICACION SOCIO
class CalificacionSocio(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=1, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )
    promedio_atraso = models.IntegerField(verbose_name="Promedio Atraso")

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "sc_calificacion"
        verbose_name = "Calificacion Socio"
        verbose_name_plural = "Calificacion Socios"


# ESTADO SOCIO
class EstadoSocio(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=4, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "sc_estado_socio"
        verbose_name = "Estado Socio"
        verbose_name_plural = "Estado Socios"


# SOCIO
class Socio(ModeloBase):
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="socio",
    )
    nro_socio = models.IntegerField(verbose_name="Nro. Socio", unique=True)
    persona = models.ForeignKey(
        Persona,
        verbose_name="Persona",
        on_delete=models.RESTRICT,
        related_name="persona",
    )
    fec_ingreso = models.DateField(verbose_name="Fecha Ingreso")
    fec_retiro = models.DateField(verbose_name="Fecha Retiro", null=True, blank=True)
    estado_socio = models.ForeignKey(
        EstadoSocio,
        verbose_name="Estado Socio",
        on_delete=models.RESTRICT,
        related_name="socio",
    )
    calificacion = models.ForeignKey(
        CalificacionSocio,
        verbose_name="Calificacion",
        on_delete=models.RESTRICT,
        related_name="socio",
    )
    comentario = models.CharField(
        verbose_name="Comentario", max_length=100, null=True, blank=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_socio, self.persona)

    def toJSON(self):
        item = model_to_dict(self)
        item["persona"] = str(self.persona)
        item["ci"] = self.persona.ci
        item["telefono"] = self.persona.telefono
        item["fec_ingreso"] = (
            self.fec_ingreso.strftime("%d/%m/%Y") if self.fec_ingreso else None
        )
        item["fec_retiro"] = (
            self.fec_retiro.strftime("%d/%m/%Y") if self.fec_retiro else None
        )
        return item

    class Meta:
        db_table = "sc_socio"
        verbose_name = "Socio"
        verbose_name_plural = "Socios"


# SOLICITUD INGRESO
class SolicitudIngreso(ModeloBase):
    nro_solicitud = models.CharField(
        verbose_name="Nro. Solicitud",
        db_column="nro_solicitud",
        max_length=10,
        unique=True,
    )
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="solicitud",
    )
    persona = models.ForeignKey(
        Persona,
        verbose_name="Persona",
        on_delete=models.RESTRICT,
        related_name="solicitud",
    )
    promocion = models.ForeignKey(
        PromocionIngreso,
        verbose_name="Promocion",
        on_delete=models.RESTRICT,
        related_name="solicitud",
    )
    fec_solicitud = models.DateField(verbose_name="Fecha Solicitud")
    fec_charla = models.DateField(verbose_name="Fecha Charla", null=True, blank=True)
    socio_proponente = models.ForeignKey(
        Socio,
        verbose_name="Socio Proponente",
        on_delete=models.RESTRICT,
        related_name="solicitud_proponente2",
        null=True,
        blank=True,
    )
    telefono = models.CharField(
        verbose_name="Teléfono", max_length=20, null=True, blank=True
    )
    direccion = models.CharField(
        verbose_name="Dirección", max_length=100, null=True, blank=True
    )
    nro_acta = models.CharField(
        verbose_name="Nro. Acta", max_length=10, null=True, blank=True
    )
    autorizado_por = models.CharField(
        verbose_name="Autorizado por", max_length=100, null=True, blank=True
    )
    socio = models.ForeignKey(
        Socio,
        verbose_name="Socio",
        on_delete=models.RESTRICT,
        related_name="solicitud",
        null=True,
        blank=True,
    )
    nro_socio = models.CharField(
        verbose_name="Nro. Socio", max_length=15, null=True, blank=True
    )
    aprobado = models.BooleanField(
        verbose_name="Aprobado", null=True, blank=True, default=None
    )
    motivo_rechazo = models.CharField(
        verbose_name="Motivo Rechazo", max_length=50, null=True, blank=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_solicitud, self.persona)

    def toJSON(self):
        item = model_to_dict(self)
        item["ci"] = self.persona.ci
        item["persona"] = str(self.persona)
        item["fec_solicitud"] = (
            self.fec_solicitud.strftime("%d/%m/%Y") if self.fec_solicitud else None
        )
        item["fec_charla"] = (
            self.fec_charla.strftime("%d/%m/%Y") if self.fec_charla else None
        )
        return item

    class Meta:
        db_table = "sc_solicitud_ingreso"
        verbose_name = "Solicitud Ingreso"
        verbose_name_plural = "Solicitudes Ingreso"


# TIPO CUENTA
class TipoCuenta(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=3, primary_key=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "sc_tipo_cuenta"
        verbose_name = "Tipo Cuenta"
        verbose_name_plural = "Tipos de Cuentas"


# OBLIGACIONES
class ObligacionCuenta(ModeloBase):
    tip_cuenta = models.ForeignKey(
        TipoCuenta,
        verbose_name="Tipo Cuenta",
        db_column="tip_cuenta",
        on_delete=models.RESTRICT,
        related_name="obligacion",
    )
    anho = models.IntegerField(verbose_name="Anho Obligacion")
    mes_desde = models.IntegerField(verbose_name="Desde Mes")
    mes_hasta = models.IntegerField(verbose_name="Hasta Mes")
    mto_cuota_mensual = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name="Monto Cuota Mensual"
    )

    def __str__(self):
        return "{}".format(self.tip_cuenta)

    class Meta:
        db_table = "sc_obligacion_cuenta"
        verbose_name = "Obligacion Aporte"
        verbose_name_plural = "Obligacion Aportes"


# CUENTA APORTES
class CuentaAporte(ModeloBase):
    # Monto Aporte Ingreso se refiere a los aportes de los socios en la constituccion de la sociedad (Nuevos Socios)
    # Monto Aporte Social se refiere a los aportes sociales
    socio = models.ForeignKey(
        Socio,
        verbose_name="Socio",
        on_delete=models.RESTRICT,
        related_name="cuenta_aporte",
    )
    mto_deuda_aporte_ingreso = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Deuda Aporte Ingreso",
        default=0,
    )
    mto_pagado_aporte_ingreso = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Pagado Aporte Inicial",
        default=0,
    )
    mto_deuda_aporte_social = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Deuda Aporte Social",
        default=0,
    )
    mto_pagado_aporte_social = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Pagado Aporte Social",
        default=0,
    )
    mto_pagado_aporte_extra = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Pagado Aporte Extraordinario",
        default=0,
    )
    mto_pagado_excedentes = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Pagado Aporte Extraordinario",
        default=0,
    )
    mto_deuda_solidaridad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Deuda Solidaridad",
        default=0,
    )
    mto_pagado_solidaridad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Pagado Solidaridad",
        default=0,
    )
    mto_ajuste_aporte = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Ajuste Aporte ",
        default=0,
    )
    mto_ajuste_solidaridad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Ajuste Solidaridad",
        default=0,
    )
    fec_pagado_hasta_aporte = models.DateField(
        verbose_name="Pago Aporte hasta fecha", null=True, blank=True
    )
    fec_pagado_hasta_solidaridad = models.DateField(
        verbose_name="Pago Solidaridad hasta fecha", null=True, blank=True
    )

    class Meta:
        db_table = "sc_cuenta_aporte"
        verbose_name = "Cuenta Aporte"
        verbose_name_plural = "Cuenta Aportes"
