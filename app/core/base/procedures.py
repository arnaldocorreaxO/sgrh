import json

import pyodbc
from django.db import connection

from config import settings
from core.base.utils import TEXTO


# EXECUTE PROCEDURE BASE
def SP_EXECUTE(sql, params=None, all=False):
    """
    sql: Sentencia SQL, PROCEDURES, FUNCTIONS
    params: Parametros de la sentencia, WHERE, PARAMETERS (los parametros tambien se puede construir en el SQL)
    all: retonar todos los registros
    debug: print sentencias y datos para debuggear
    """
    debug = settings.DEBUGXO
    results = {}
    # Presql es necesario para que funcione correctamente los procedimientos
    # Formato de fecha dmy hay que enviar siempre para el correcto proceso de las fechas
    presql = """
    SET DATEFORMAT dmy;
    SET NOCOUNT ON;
    """
    sql = presql + sql

    if debug:
        print("SENTENCIA SQL")
        print(sql)
        print("PARAMETROS")
        print(params)

    def dictfetchall(cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([str(col[0]).lower() for col in desc], row))
            for row in cursor.fetchall()
        ]

    try:
        cursor = connection.cursor()
        # Execute Stored Procedure With Parameters
        cursor.execute(sql, params)
        # Soluciona el problema de No results.  Previous SQL was not a query.
        if cursor.description:
            # rows = cursor.fetchall()
            rows = dictfetchall(cursor)
        else:
            while cursor.nextset():
                try:
                    # rows = cursor.fetchall()
                    rows = dictfetchall(cursor)
                    break
                except pyodbc.ProgrammingError:
                    continue
        results = rows if all else rows[0]

        # DEBUGGEAR
        if debug:
            print("DICTIONARY")
            print(results)
            print("JSON")
            # default=str -> Evita Object of type Decimal is not JSON serializable
            print(json.dumps(results, default=str))
    except Exception as e:
        print(str(e))
        results["error"] = str(e)
    finally:
        cursor.close()
        del cursor
    # RETORNAMOS EL RESULTADO COMO DICT Y EN LA VIEWS RETORNAMOS COMO JSON
    return results


# OBTENER RUC
def fnCALCULAR_RUC(ci):
    # Define variables
    try:
        # Declare variables
        p_numero = ci
        p_basemax = None
        # Prepare the stored procedure execution script and parameter values
        storedProc = f"SELECT [dbo].[fnCALCULAR_DV_11_A] (%s,%s) AS RUC"
        params = (p_numero, p_basemax)
        data = SP_EXECUTE(storedProc, params)
        data = str(p_numero) + "-" + str(data["ruc"] or "")
        return data
    except Exception as e:
        print(e)


# RECUPERA DATOS PERSONALES DE LA BD DE IDENTIFICACIONES
def sp_identificaciones(**kwargs):
    # Define variables
    try:
        params = {}
        params["ci"] = TEXTO(kwargs["ci"])
        params["ruc"] = TEXTO(fnCALCULAR_RUC(kwargs["ci"]))

        # Prepare the stored procedure execution script and parameter values
        # print(params)
        storedProc = f"""   DECLARE @RC int
                            DECLARE @P_CI varchar(20)
                            DECLARE @P_RUC varchar(20)

                            -- TODO: Establezca los valores de los parámetros aquí.

                            EXECUTE @RC = [dbo].[PA_IDENTIFICACIONES] 
                             @P_CI = {params['ci']}
                            ,@P_RUC = {params['ruc']};            

                        """

        return SP_EXECUTE(storedProc, all=True)
    except Exception as e:
        print(e)
