import json

from django.http import JsonResponse

from core.base.models import Persona, Sucursal
from core.base.procedures import SP_EXECUTE
from core.base.utils import TEXTO, YYYY_MM_DD
from core.socio.models import Socio


def sp_alta_solicitud_prestamo(request):
    cod_usuario = request.user.cod_usuario
    params = {}
    params["sucursal"] = request.POST["sucursal"]
    params["socio"] = request.POST["socio"]
    params["tipo_prestamo"] = request.POST["tipo_prestamo"]
    params["fec_solicitud"] = TEXTO(YYYY_MM_DD(request.POST["fec_solicitud"]))
    params["destino_prestamo"] = request.POST["destino_prestamo"]
    params["monto_solicitado"] = request.POST["monto_solicitado"]
    params["monto_prestamo"] = request.POST["monto_prestamo"]
    params["plazo_mes"] = request.POST["plazo_mes"]
    params["moneda"] = request.POST["moneda"]
    params["tasa_interes"] = request.POST["tasa_interes"]
    params["cant_cuota"] = request.POST["cant_cuota"]
    params["monto_cuota_inicial"] = request.POST["monto_cuota_inicial"]
    params["fec_desembolso"] = TEXTO(YYYY_MM_DD(request.POST["fec_desembolso"]))
    params["fec_primer_vto"] = TEXTO(YYYY_MM_DD(request.POST["fec_primer_vto"]))
    params["total_interes"] = request.POST["total_interes"]
    params["monto_neto"] = request.POST["monto_neto"]
    params["usu_actual"] = request.user.id
    params["cod_forma_desembolso"] = TEXTO(request.POST["cod_forma_desembolso"])
    params["monto_refinanciado"] = request.POST["monto_refinanciado"]

    print(params)
    storedProc = f"""  
                    SET NOCOUNT ON;
                    DECLARE @RC int
                    DECLARE @SUCURSAL_ID numeric(5,0)
                    DECLARE @SOCIO_ID numeric(6,0)
                    DECLARE @NRO_SOLICITUD char(10)
                    DECLARE @TIPO_PRESTAMO_ID numeric(5,0)
                    DECLARE @FEC_SOLICITUD datetime
                    DECLARE @DESTINO_PRESTAMO_ID numeric(5,0)
                    DECLARE @MONTO_SOLICITADO numeric(14,2)
                    DECLARE @MONTO_PRESTAMO numeric(14,2)
                    DECLARE @PLAZO_MES numeric(5,0)
                    DECLARE @MONEDA_ID numeric(5,0)
                    DECLARE @TASA_INTERES numeric(7,2)
                    DECLARE @CANT_CUOTA numeric(5,0)
                    DECLARE @MONTO_CUOTA_INICIAL numeric(14,2)
                    DECLARE @FEC_DESEMBOLSO datetime
                    DECLARE @FEC_PRIMER_VTO datetime
                    DECLARE @TOTAL_INTERES numeric(12,2)
                    DECLARE @COD_TIPO_DCTO numeric(5,0)
                    DECLARE @TOTAL_GASTOS numeric(14,2)
                    DECLARE @TOTAL_DESCUENTOS numeric(14,2)
                    DECLARE @MONTO_NETO numeric(14,2)
                    DECLARE @CANT_CUOTA_EXTRAORDINARIO numeric(5,0)
                    DECLARE @MONTO_AMORTIZACION numeric(12,2)
                    DECLARE @FEC_1RA_AMORTIZACION char(10)
                    DECLARE @PERIODO_AMORTIZACION numeric(5,0)
                    DECLARE @COND_LIQUIDACION numeric(5,0)
                    DECLARE @USU_INSERCION numeric(4,0)
                    DECLARE @INGRESO_FAMILIAR numeric(12,2)
                    DECLARE @COD_GRUPO_PRESTAMO numeric(5,0)
                    DECLARE @COD_TIPO_LINEA_CREDITO numeric(8,0)
                    DECLARE @COD_FORMA_DESEMBOLSO numeric(5,0)
                    DECLARE @COD_CTA_AHORRO numeric(10,0)
                    DECLARE @MONTO_REFINANCIADO numeric(14,2)
                    DECLARE @SUSCRIPCION_ADESCONTAR numeric(14,2)
                    DECLARE @CUO_GRACIA_INT_REF numeric(3,0)
                    DECLARE @CNT_CUO_INT_REF numeric(3,0)
                    DECLARE @COD_COMERCIO int
                    DECLARE @MENSAJE varchar(100)
                    DECLARE @MSG varchar(100)
                    DECLARE @NRO_SOL_GEN varchar(10) --NRO. SOLICITUD GENERADA

    -- TODO: Establezca los valores de los parámetros aquí.

    EXECUTE @RC = [dbo].[PA_ALTA_SOLICITUD_PRESTAMO] 
                     @SUCURSAL_ID={params['sucursal']}
                    ,@SOCIO_ID={params['socio']}
                    ,@NRO_SOLICITUD=@NRO_SOL_GEN OUTPUT
                    ,@TIPO_PRESTAMO_ID={params['tipo_prestamo']}
                    ,@FEC_SOLICITUD={params['fec_solicitud']}
                    ,@DESTINO_PRESTAMO_ID={params['destino_prestamo']}
                    ,@COD_TIPO_GARANTIA=NULL
                    ,@LIMITE_CREDITO=NULL
                    ,@MONTO_SOLICITADO={params['monto_solicitado']}
                    ,@MONTO_PRESTAMO={params['monto_prestamo']}
                    ,@COD_SISTEMA_CALCULO=NULL
                    ,@PLAZO_MES={params['plazo_mes']}
                    ,@MONEDA_ID={params['moneda']}
                    ,@TASA_INTERES={params['tasa_interes']}
                    ,@CANT_CUOTA={params['cant_cuota']}
                    ,@MONTO_CUOTA_INICIAL={params['monto_cuota_inicial']}
                    ,@FEC_DESEMBOLSO={params['fec_desembolso']}
                    ,@FEC_PRIMER_VTO={params['fec_primer_vto']}
                    ,@TOTAL_INTERES={params['total_interes']}
                    ,@TIPO_CUOTA=NULL
                    ,@TIPO_INTERES=NULL
                    ,@COD_TIPO_DCTO=NULL
                    ,@TOTAL_GASTOS=NULL
                    ,@TOTAL_DESCUENTOS=NULL
                    ,@MONTO_NETO={params['monto_neto']}
                    ,@CANT_CUOTA_EXTRAORDINARIO=NULL
                    ,@MONTO_AMORTIZACION=NULL
                    ,@FEC_1RA_AMORTIZACION=NULL
                    ,@PERIODO_AMORTIZACION=NULL
                    ,@COND_LIQUIDACION=NULL
                    ,@USU_INSERCION={params['usu_actual']}
                    ,@INGRESO_FAMILIAR=NULL
                    ,@COD_GRUPO_PRESTAMO=NULL
                    ,@COD_TIPO_LINEA_CREDITO=NULL
                    ,@COD_FORMA_DESEMBOLSO={params['cod_forma_desembolso']}
                    ,@COD_CTA_AHORRO=NULL
                    ,@MONTO_REFINANCIADO={params['monto_refinanciado']}
                    ,@SUSCRIPCION_ADESCONTAR=NULL
                    ,@CUO_GRACIA_INT_REF=NULL
                    ,@CNT_CUO_INT_REF=NULL
                    ,@COD_COMERCIO=NULL                      
                    ,@MENSAJE=@MSG OUTPUT;

    SELECT @RC AS RTN, @MSG AS MSG,@NRO_SOL_GEN AS VAL;
    """

    print(storedProc)
    # Usamos un operador de desempaquetado iterable con coma final, para pasar la lista params como tupla
    # Ej.    lista = [10,20,30]
    #        tupla = (*lista,)
    # return SP_EXECUTE(storedProc, (*params,))
    return SP_EXECUTE(storedProc)


def sp_aprobar_solicitud_ingreso(request):
    # Define variables
    _COD_USUARIO = "ACOR"
    _DDMMYYYY = request.POST["fec_resolucion"]
    _FEC_RESOLUCION = _DDMMYYYY[6:] + "-" + _DDMMYYYY[3:5] + "-" + _DDMMYYYY[:2]
    _NRO_ACTA = request.POST["nro_acta"]
    _APROBADO = request.POST["aprobado"]
    _AUTORIZADO_POR = request.POST["autorizado_por"]
    _NRO_SOLICITUD = request.POST["nro_solicitud"]
    _MOTIVO_RECHAZO = request.POST["motivo_rechazo"]
    _NRO_SOCIO = request.POST["nro_socio"]
    _MENSAJE = None
    # Prepare the stored procedure execution script and parameter values

    params = (
        _COD_USUARIO,
        _FEC_RESOLUCION,
        _NRO_ACTA,
        _APROBADO,
        _AUTORIZADO_POR,
        _NRO_SOLICITUD,
        _MOTIVO_RECHAZO,
        _NRO_SOCIO,
    )
    print(params)
    storedProc = f"""  
                        SET NOCOUNT ON;
                        DECLARE @RC int
                        DECLARE @COD_USUARIO varchar(4)
                        DECLARE @FEC_RESOLUCION datetime
                        DECLARE @NRO_ACTA varchar(20)
                        DECLARE @APROBADO bit
                        DECLARE @MOTIVO_RECHAZO varchar(50)
                        DECLARE @NRO_SOLICITUD char(10)
                        DECLARE @NRO_SOCIO varchar(10)
                        DECLARE @AUTORIZADO_POR varchar(100)
                        DECLARE @MENSAJE varchar(100)
                        DECLARE @OUT varchar(100)

                        EXECUTE @RC = [dbo].[PA_APROBAR_SOLICITUD_SOCIO] 
                         @COD_USUARIO=%s
                        ,@FEC_RESOLUCION=%s
                        ,@NRO_ACTA=%s
                        ,@APROBADO=%s
                        ,@AUTORIZADO_POR=%s
                        ,@NRO_SOLICITUD=%s                        
                        ,@MOTIVO_RECHAZO=%s     
                        ,@NRO_SOCIO=%s                   
                        ,@MENSAJE=@OUT OUTPUT;
                     
                        SELECT @RC AS return_value;
                        SELECT @OUT AS output_value;
                    """

    # Execute Stored Procedure With Parameters
    return SP_EXECUTE(storedProc, params)
