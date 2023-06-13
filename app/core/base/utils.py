def choice_anho():
    from datetime import datetime

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


def get_primer_fecha_mes():
    from datetime import datetime, timedelta

    return (datetime.now() - timedelta(days=datetime.now().day - 1)).strftime(
        "%d/%m/%Y"
    )


def get_fecha_actual():
    from datetime import datetime

    # today = datetime.today()
    # return datetime.date(year=today.year-1, month=today.month, day=today.day)
    return datetime.now().strftime("%d/%m/%Y")


def get_mes_actual():
    from datetime import datetime

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
