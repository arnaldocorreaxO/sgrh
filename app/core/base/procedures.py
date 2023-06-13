import json

import pyodbc
from django.db import connection


def SP_EXECUTE(sql, params=None):
    results = {}
    # Presql es necesario para que funcione correctamente los procedimientos
    # Formato de fecha dmy hay que enviar siempre para el correcto proceso de las fechas
    presql = """
    SET DATEFORMAT dmy;
    SET NOCOUNT ON;
    """
    sql = presql + sql
    print("SENTENCIA SQL")
    print(sql)
    print("PARAMETROS")
    print(params)
    try:
        cursor = connection.cursor()
        # Execute Stored Procedure With Parameters
        cursor.execute(sql, params)
        # Soluciona el problema de No results.  Previous SQL was not a query.
        if cursor.description:
            rows = cursor.fetchall()
        else:
            while cursor.nextset():
                try:
                    rows = cursor.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
        while rows:
            for row in rows:
                print("rtn: ", row[0])
                print("msg: ", row[1])
                print("val: ", row[2])
                results["rtn"] = row[0]
                results["msg"] = row[1]
                results["val"] = row[2]

            if cursor.nextset():
                rows = cursor.fetchall()
            else:
                rows = None
        print("DICTIONARY")
        print(results)
        print("JSON")
        print(json.dumps(results, default=str))
        # default=str -> Evita Object of type Decimal is not JSON serializable
    except Exception as e:
        print(str(e))
        results["error"] = str(e)
    finally:
        cursor.close()
        del cursor
    # RETORNAMOS EL RESULTADO COMO DICT Y EN LA VIEWS RETORNAMOS COMO JSON
    return results
