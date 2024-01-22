from datetime import date, datetime, timedelta


# LLAMAR SIN PARENTESIS PARA OBTENER LA FECHA Y HORA ACTUAL
def choice_anho():
    vAnhoActual = datetime.now().year
    CHOICE = [(str(x), str(x)) for x in range(vAnhoActual, vAnhoActual - 10, -1)]
    return CHOICE


def choice_mes():
    CHOICE = [
        ("1", "Enero"),
        ("2", "Febrero"),
        ("3", "Marzo"),
        ("4", "Abril"),
        ("5", "Mayo"),
        ("6", "Junio"),
        ("7", "Julio"),
        ("8", "Agosto"),
        ("9", "Setiembre"),
        ("10", "Octubre"),
        ("11", "Noviembre"),
        ("12", "Diciembre"),
    ]
    return CHOICE


# LLAMAR SIN PARENTESIS PARA OBTENER LA FECHA Y HORA ACTUAL
def get_primer_fecha_mes():
    return (datetime.now() - timedelta(days=datetime.now().day - 1)).strftime(
        "%d/%m/%Y"
    )


# LLAMAR SIN PARENTESIS PARA OBTENER LA FECHA Y HORA ACTUAL
def get_fecha_actual():
    # today = datetime.today()
    # return datetime.date(year=today.year-1, month=today.month, day=today.day)
    return datetime.now().strftime("%d/%m/%Y")


# LLAMAR SIN PARENTESIS PARA OBTENER LA FECHA Y HORA ACTUAL
def get_fecha_actual_ymd():
    # today = datetime.today()
    # return datetime.date(year=today.year-1, month=today.month, day=today.day)
    return datetime.now().strftime("%Y-%m-%d")


# LLAMAR SIN PARENTESIS PARA OBTENER LA FECHA Y HORA ACTUAL
def get_fecha_hora_actual():
    # today = datetime.today()
    # return datetime.date(year=today.year-1, month=today.month, day=today.day)
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# LLAMAR SIN PARENTESIS PARA OBTENER LA FECHA Y HORA ACTUAL
def get_mes_actual():
    return datetime.now().month


# CONVIERTE FECHA DD/MM/YYYY A YYYY-MM-DD
def YYYY_MM_DD(ddmmyyyy):
    import datetime

    return datetime.datetime.strptime(ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%d")
    # Metodo xO :)
    # return ddmmyyyy[6:] + "-" + ddmmyyyy[3:5] + "-" + ddmmyyyy[:2] if ddmmyyyy else ""


# CONCATENA COMILLAS SIMPLES AL INICIO Y AL FINAL DE UN DATO
# Ej. recibe 2023-03-01 retorna '2023-03-01', recibe 1 retorna '1'
def TEXTO(dato):
    if dato:
        return f"'{str(dato)}'"
    return "NULL"


# Equivalente a La función ISNULL () de SQL Server reemplaza NULL con un valor especificado
def isNULL(expression, replacement=None):
    return expression if expression else replacement


# RESETEA LOS CAMPOS NUMERICOS LOCALIZADOS (LOCALIZED_FIELDS) SETEADO EN LOS FORMS
# REEMPLAZA PUNTO (.) Y COMA (,) DECIMAL
# RECIBE 123.123.123,99 RETORNA 123123123.99
def RESET_FORMATO(expression):
    return str(expression).replace(".", "").replace(",", ".")


# Calcular edad
def calculate_age(born):
    today = date.today()
    # ((today.month, today.day) < (born.month, born.day)) That can be done much simpler
    # considering that int(True) is 1 and int(False) is 0:
    return (today.year - born.year) - (
        (today.month, today.day) < (born.month, born.day)
    )
