from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

def validar_mayor_edad(fecha_str):
	try:
		# Convertimos el string a objeto date
		nacimiento = datetime.strptime(fecha_str, "%Y-%m-%d").date()
		
		# OBTENER LA FECHA REAL DE HOY (Se ejecuta cada vez que se llama a la función)
		hoy = date.today() 
		
		# Calculamos la diferencia
		edad = relativedelta(hoy, nacimiento)
		
		return edad.years >= 18
	except Exception:
		return False

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


# Calcular edad detallada en años, meses y días con dateutil
def calculate_age_detailed(born):
    today = date.today()
    diferencia = relativedelta(today, born)
    return diferencia.years, diferencia.months, diferencia.days

# Ejemplo de uso:
# años, meses, dias = calculate_age_detailed(fecha_nacimiento)

# Calcular edad detallada en años, meses y días con lógica manual
def calculate_age_detailed2(born):
    today = date.today()
    
    # 1. Diferencia inicial
    years = today.year - born.year
    months = today.month - born.month
    days = today.day - born.day

    # 2. Ajuste de días negativos
    if days < 0:
        # Retroceder un mes y sumar los días del mes anterior
        months -= 1
        # Obtenemos el último día del mes pasado
        # (Usamos una fecha temporal para el cálculo)
        import calendar
        month_to_check = today.month - 1 if today.month > 1 else 12
        year_to_check = today.year if today.month > 1 else today.year - 1
        _, last_day_prev_month = calendar.monthrange(year_to_check, month_to_check)
        days += last_day_prev_month

    # 3. Ajuste de meses negativos
    if months < 0:
        years -= 1
        months += 12

    return years, months, days