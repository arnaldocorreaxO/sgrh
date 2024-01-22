from core.base.models import Persona, Sucursal
from core.base.procedures import SP_EXECUTE
from core.base.utils import TEXTO, YYYY_MM_DD


def sp_validar_solicitud_ingreso(request):
    # Define variables
    params = {}
    params["cod_usuario"] = TEXTO(request.user.cod_usuario)
    params["fec_solicitud"] = TEXTO(request.POST["fec_solicitud"])
    params["cod_sucursal"] = request.POST["sucursal"]
    params["nro_documento"] = (
        Persona.objects.filter(id=request.POST["persona"]).first().ci
    )

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   DECLARE @RC int
                        DECLARE @COD_USUARIO varchar(4)
                        DECLARE @NRO_SOLICITUD char(10)
                        DECLARE @COD_SUCURSAL varchar(5)
                        DECLARE @NRO_DOCUMENTO numeric(12,0)
                        DECLARE @FEC_SOLICITUD datetime
                        DECLARE @MENSAJE varchar(100)
                        DECLARE @MSG varchar(100)
                        DECLARE @NRO_SOL_GEN varchar(10) --NRO. SOLICITUD GENERADA

                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXECUTE @RC = [dbo].[PA_VALIDAR_SOLICITUD_SOCIO] 
                         @COD_USUARIO={params['cod_usuario']}
                        ,@FEC_SOLICITUD={params['fec_solicitud']}
                        ,@NRO_SOLICITUD=@NRO_SOL_GEN OUTPUT
                        ,@COD_SUCURSAL={params['cod_sucursal']}
                        ,@NRO_DOCUMENTO={params['nro_documento']}     
                        ,@MENSAJE=@MSG OUTPUT;

                        SELECT @RC AS RTN, @MSG AS MSG,@NRO_SOL_GEN AS VAL;
                    """

    return SP_EXECUTE(storedProc)


def sp_aprobar_solicitud_ingreso(request):
    # Define variables
    params = {}
    params["cod_usuario"] = TEXTO(request.user.cod_usuario)
    params["fec_resolucion"] = TEXTO(request.POST["fec_resolucion"])
    params["nro_acta"] = TEXTO(request.POST["nro_acta"])
    params["aprobado"] = TEXTO(request.POST["aprobado"])
    params["autorizado_por"] = TEXTO(request.POST["autorizado_por"])
    params["nro_solicitud"] = TEXTO(request.POST["nro_solicitud"])
    params["motivo_rechazo"] = TEXTO(request.POST["motivo_rechazo"])
    params["nro_socio"] = TEXTO(request.POST["nro_socio"])

    # Prepare the stored procedure execution script and parameter values
    storedProc = f"""   DECLARE @RC int
                        DECLARE @COD_USUARIO varchar(4)
                        DECLARE @FEC_RESOLUCION datetime
                        DECLARE @NRO_ACTA varchar(20)
                        DECLARE @APROBADO NUMERIC(1)
                        DECLARE @MOTIVO_RECHAZO varchar(50)
                        DECLARE @NRO_SOLICITUD char(10)
                        DECLARE @NRO_SOCIO varchar(10)
                        DECLARE @AUTORIZADO_POR varchar(100)
                        DECLARE @MENSAJE varchar(100)
                        DECLARE @MSG varchar(100) --COMENTARIO

                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXECUTE @RC = [dbo].[PA_APROBAR_SOLICITUD_SOCIO] 
                        @COD_USUARIO={params['cod_usuario']}
                        ,@FEC_RESOLUCION={params['fec_resolucion']}
                        ,@NRO_ACTA={params['nro_acta']}
                        ,@APROBADO={params['aprobado']}
                        ,@AUTORIZADO_POR={params['autorizado_por']}
                        ,@NRO_SOLICITUD={params['nro_solicitud']}                     
                        ,@MOTIVO_RECHAZO={params['motivo_rechazo']}     
                        ,@NRO_SOCIO={params['nro_socio']}                
                        ,@MENSAJE=@MSG OUTPUT;
                        
                        SELECT @RC AS RTN, @MSG AS MSG,@MSG AS VAL;"""

    return SP_EXECUTE(storedProc)
