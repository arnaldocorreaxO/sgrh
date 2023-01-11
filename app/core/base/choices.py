
#ESTADO
def choiceEstado():
    CHOICE = [
        ('A' , 'ACTIVO'),
        ('I' , 'INACTIVO'),
        ('T' , 'TEMPORAL'),
    ]
    # CHOICE = tuple(RefDet.objects.filter(cod_referencia='ESTADO'))
    return CHOICE
#TIPO DEBITO CREDITO 
def choiceTipoDC():
    CHOICE = [
        ('D' , 'DEBITO'),
        ('C' , 'CREDITO'),
    ]
    return CHOICE

#SI-NO
def choiceSiNo():
    CHOICE = [
        ('S' , 'SI'),
        ('N' , 'NO'),
    ]
    return CHOICE

#NATURALEZA CONTABLE
def choiceTipoCuenta():
    CHOICE = [
        # Debe- Debito
        ('D' , 'DEUDOR'),
        # Haber - Credito
        ('C' , 'ACREEDOR'),
    ]
    return CHOICE

#CAJA DIARIO
def choiceCajaDiario():
    CHOICE = [
        # Diario
        ('D' , 'DIARIO'),
        # Caja
        ('C' , 'CAJA'),
    ]
    return CHOICE


#OPERACION SOBRE SALDO
def choiceOperacionSaldo():
    CHOICE = [
        ('R' , 'RESTA'),
        ('S' , 'SUMA'),
        ('N' , 'NINGUNA'),
    ]
    return CHOICE
