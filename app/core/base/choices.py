# GENERO
def choiceGenero():
    CHOICE = [
        ("M", "MASCULINO"),
        ("F", "FEMENINO"),
    ]
    # CHOICE = tuple(RefDet.objects.filter(cod_referencia='ESTADO'))
    return CHOICE


# ESTADO
def choiceEstado():
    CHOICE = [
        ("A", "A - ACTIVO"),
        ("I", "I - INACTIVO"),
        ("T", "T - TEMPORAL"),
    ]
    # CHOICE = tuple(RefDet.objects.filter(cod_referencia='ESTADO'))
    return CHOICE


# TIPO DEBITO CREDITO
def choiceTipoDC():
    CHOICE = [
        ("D", "D - DEBITO"),
        ("C", "C - CREDITO"),
    ]
    return CHOICE


# TIPO MODULO CONTABLE
def choiceTipoContable():
    CHOICE = [("A", "ACTIVO"), ("P", "PASIVO"), ("N", "NINGUNO")]
    return CHOICE


# INDICA UNICO O MULTIPLE DESEMBOLSO
def choiceMultipleDesembolso():
    CHOICE = [
        (1, "UNICO"),
        (2, "MULTIPLE"),
    ]
    return CHOICE


# SI-NO
def choiceSiNo():
    CHOICE = [
        ("S", "SI"),
        ("N", "NO"),
    ]
    return CHOICE


# NATURALEZA CONTABLE
def choiceTipoCuenta():
    CHOICE = [
        # Debe- Debito
        ("D", "D - DEUDOR"),
        # Haber - Credito
        ("C", "C - ACREEDOR"),
    ]
    return CHOICE


# CAJA DIARIO
def choiceCajaDiario():
    CHOICE = [
        # Diario
        ("D", "D - DIARIO"),
        # Caja
        ("C", "C - CAJA"),
    ]
    return CHOICE


# AMORTIZABLE
def choiceAmortizable():
    CHOICE = [
        ("S", "S - AMORTIZABLE"),
        ("N", "N - PAGO UNICO"),
        ("R", "R - REFINANCIADOS"),
        ("V", "V - VINCULADOS"),
        ("E", "E - EX SOCIOS"),
        ("D", "D - DESCUENDO DOCUMENTO"),
        ("Q", "Q - DEUDA DESTINO A LA VIVIENDA"),
    ]
    return CHOICE


# OPERACION SOBRE SALDO
def choiceOperacionSaldo():
    CHOICE = [
        ("R", "R - RESTA"),
        ("S", "S - SUMA"),
        ("N", "N - NINGUNA"),
    ]
    return CHOICE


# METODO DE INTERES
def choiceMetodoInteres():
    CHOICE = [
        ("D", "D - METODO DEVENGADO"),
        ("C", "C - METODO COBRADOR"),
        ("A", "A - AMBOS"),
    ]
    return CHOICE


# TIPO ACCESO TRANSACCION
def choiceTipoAcceso():
    CHOICE = [
        ("C", "C- CAJA"),
        ("D", "D - DIARIO"),
        ("N", "N - NINGUNA"),
    ]
    return CHOICE
