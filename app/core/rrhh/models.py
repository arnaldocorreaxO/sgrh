import os

from django.core.validators import FileExtensionValidator
from django.utils import timezone


from core.base.models import Barrio, Ciudad, Moneda, Pais, RefDet
from core.models import ModeloBase
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import model_to_dict

from core.base.choices import *
from core.base.utils import calculate_age
from core.user.models import User

def empleado_directory_path(instance, filename, seccion):
    # seccion: DOCUMENTO, FORMACION, CURSOS, LABORAL, COMPLEMENTARIOS
    return f'empleado/DOCUMENTO/{instance.empleado.ci}/{seccion}/{filename}'

# INSTITUCION
class Institucion(ModeloBase):
    codigo = models.CharField(max_length=255, unique=True)
    denominacion = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=100)  
    tipo_institucion = models.ForeignKey(RefDet, on_delete=models.RESTRICT, related_name="tipo_institucion_institucion",null=True, blank=True)
    tipo_funcion = models.ForeignKey(RefDet, on_delete=models.RESTRICT, related_name="tipo_funcion_institucion",null=True, blank=True)
    
    def __str__(self):  
        return F"{self.denominacion} - {self.abreviatura}"
    
    class Meta:
        db_table = "rh_institucion"
        verbose_name = "001 - Institución"
        verbose_name_plural = "001 -Instituciones" 

# SEDE 
class Sede(ModeloBase):
    institucion = models.ForeignKey(Institucion, on_delete=models.RESTRICT)
    codigo = models.CharField(max_length=255, unique=True)
    denonimacion = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=100)  

    def __str__(self):  
        return self.denonimacion

    class Meta:
        db_table = "rh_sede"
        verbose_name = "002 - Sede"
        verbose_name_plural = "002 - Sedes" 

# DEPENDENCIA = DEPARTAMENTO, AREA, SECCION
class Dependencia(ModeloBase):
    sede = models.ForeignKey(Sede, on_delete=models.RESTRICT)
    codigo = models.CharField(max_length=255, unique=True)
    denonimacion = models.CharField(max_length=255)
    dependencia_padre = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self):  
        return self.denonimacion

    class Meta:
        db_table = "rh_dependencia"
        verbose_name = "003 - Dependencia"
        verbose_name_plural = "003 - Dependencias" 
        ordering = ['id']

# CATEGORIA SALARIAL
class CategoriaSalarial(ModeloBase):
    codigo = models.CharField(max_length=4,unique=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.RESTRICT)
    denominacion = models.CharField(max_length=150, verbose_name="Denominación")   

    def __str__(self):
       return f"{self.codigo}"

    class Meta:
        db_table = "rh_categoria_salarial"
        verbose_name = "010 - Categoría Salarial"
        verbose_name_plural = "010 - Categorías Salariales"
        ordering = ['id']

class CategoriaSalarialVigencia(ModeloBase):
    categoria = models.ForeignKey(
        CategoriaSalarial,
        on_delete=models.CASCADE,
        related_name="vigencias"
    )
    fecha_vigencia = models.DateField(
        default=timezone.now,verbose_name="Fecha de Vigencia"        
    )
    sueldo_basico = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.categoria.codigo} - {self.fecha_vigencia} - {self.sueldo_basico}"

    class Meta:
        db_table = "rh_categoria_salarial_vigencia"
        verbose_name = "011 - Vigencia de Categoría Salarial"
        verbose_name_plural = "011 - Vigencias de Categorías Salariales"
        ordering = ["-fecha_vigencia","-sueldo_basico"]
        unique_together = ("categoria", "fecha_vigencia")

# Nivel Jerarquico, Cargo, Puesto
class Nivel(ModeloBase):
    denominacion = models.CharField(max_length=150, verbose_name="Denominación")
    # categoria = models.ForeignKey(CategoriaSalarial, on_delete=models.RESTRICT, related_name="nivel_categoria",null=True, blank=True)
    
    def __str__(self):
        return f"{self.denominacion}"

    class Meta:
        db_table = "rh_nivel"
        verbose_name = "020 - Nivel"
        verbose_name_plural = "020 - Niveles"
        ordering = ['id']

class MatrizSalarial(ModeloBase):
    nivel = models.ForeignKey(Nivel, on_delete=models.RESTRICT, related_name="matriz_nivel")
    categoria = models.ForeignKey(CategoriaSalarial, on_delete=models.RESTRICT, related_name="matriz_categoria",null=True, blank=True)
    denominacion = models.CharField(max_length=150, verbose_name="Denominación",null=True)

    def __str__(self):
        return f"{self.nivel} - {self.categoria} -{self.denominacion}"

    class Meta:
        db_table = "rh_matriz_salarial"
        verbose_name = "021 - Matriz Salarial"
        verbose_name_plural = "021 - Matrices Salariales"
        ordering = ['id']

class CargoPuesto(ModeloBase):
    matriz_salarial = models.ForeignKey(MatrizSalarial, on_delete=models.RESTRICT, related_name="matriz_salarial", null=True, blank=True)
    denominacion = models.CharField(max_length=150, verbose_name="Denominación")    
    
    def __str__(self):
        return f"{self.denominacion} - {self.matriz_salarial.categoria if self.matriz_salarial else ''}"

    class Meta:
        db_table = "rh_cargo_puesto"
        verbose_name = "022 - Cargo Puesto"
        verbose_name_plural = "022 - Cargos Puestos"
        ordering = ['id']

# EMPLEADO
class Empleado(ModeloBase):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    legajo = models.CharField(
        verbose_name="Legajo", max_length=4, validators=[MinLengthValidator(4)],null=True, blank=True
    )
    ci = models.BigIntegerField(verbose_name="CI", unique=True)
    ruc = models.CharField(
        verbose_name="RUC",
        max_length=10,
        validators=[MinLengthValidator(6)],
        unique=True,
        null=True,
        blank=True,
    )
    nombre = models.CharField(verbose_name="Nombre", max_length=150)
    apellido = models.CharField(verbose_name="Apellido", max_length=150)
    nacionalidad = models.ForeignKey(
        Pais, verbose_name="Nacionalidad", on_delete=models.RESTRICT
    )
    ciudad = models.ForeignKey(
        Ciudad, verbose_name="Ciudad", on_delete=models.RESTRICT
    )
    barrio = models.ForeignKey(
        Barrio, verbose_name="Barrio", on_delete=models.RESTRICT, null=True, blank=True
    )
    direccion = models.CharField(
        verbose_name="Dirección", max_length=100, null=True, blank=True
    )
    telefono = models.CharField(
        verbose_name="Teléfono", max_length=20, null=True, blank=True
    )
    celular = models.CharField(
        verbose_name="Celular", max_length=20
    )
    email = models.CharField(max_length=50, verbose_name="Email")
    fec_nacimiento = models.DateField(verbose_name="Fecha Nacimiento", null=True)
    sexo = models.ForeignKey(
        RefDet,
        verbose_name="Sexo",
        db_column="sexo",
        on_delete=models.RESTRICT,
        related_name="sexo_empleado",
    )
    estado_civil = models.ForeignKey(
        RefDet,
        verbose_name="Estado Civil",
        db_column="estado_civil",
        on_delete=models.RESTRICT,
        related_name="estado_civil_empleado",
    )
    # tipo_sanguineo = models.ForeignKey(
    #     RefDet,
    #     verbose_name="Tipo Sanguíneo",
    #     on_delete=models.RESTRICT,
    #     related_name="tipo_sanguineo_empleado",null=True, blank=True
    # )

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_edad(self):
        return calculate_age(self.fec_nacimiento)

    def toJSON(self):
        item = model_to_dict(self)
        item["edad"] = self.get_edad()
        return item

    class Meta:
        db_table = "rh_empleado"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        unique_together = ("legajo", "ci")
        permissions = [
            ("view_empleado_self", "Puede ver su propio perfil"),
            ("add_empleado_self", "Puede agregar su propio perfil"),
            ("change_empleado_self", "Puede modificar su propio perfil"),
            ("delete_empleado_self", "Puede eliminar su propio perfil"),            
        ]

# DEPENDENCIA POSICION = CARGO  
class DependenciaPosicion(ModeloBase):
    dependencia=models.ForeignKey(Dependencia, on_delete=models.RESTRICT)
    posicion=models.ForeignKey(CargoPuesto, on_delete=models.RESTRICT)

    def __str__(self):  
        return f"{self.posicion} - {self.dependencia}"

    class Meta:
        db_table = "rh_dependencia_posicion"
        verbose_name = "Dependencia Posicion"
        verbose_name_plural = "Dependencias Posiciones" 

# EMPLEADO POSICION = ASIGNACION DE CARGO PUESTO
class EmpleadoPosicion(ModeloBase):
    def directory_path(instance, filename):
        return f'empleado/{instance.empleado.ci}/DOC/RESOLUCION/{filename}'    
    
    legajo=models.CharField(max_length=4, unique=True)
    empleado=models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    dependencia_posicion=models.ForeignKey(DependenciaPosicion, on_delete=models.RESTRICT)
    fecha_inicio=models.DateField(verbose_name="Fecha Inicio") 
    fecha_fin=models.DateField(verbose_name="Fecha Fin", null=True, blank=True)    
    vinculo_laboral=models.ForeignKey(
        RefDet,on_delete=models.RESTRICT, related_name="vinculo_laboral_empleado_posicion"
    )
    archivo_pdf = models.FileField(
        upload_to=directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",null=True, blank=True
    )
    estado_empleado_posicion = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        verbose_name="Estado en la Posición",
        db_column="estado_empleado_posicion",
        on_delete=models.RESTRICT,
        related_name="estado_empleado_posicion",
        default="S", # Activo
    )  
    def __str__(self):
        return f"{self.empleado} - {self.dependencia_posicion}"
    class Meta:
        db_table = "rh_empleado_posicion"
        verbose_name = "Asignación de Cargo"
        verbose_name_plural = "Asignaciones de Cargos" 
        ordering = ['-fecha_inicio']

# ANTECEDENTES ACADEMICOS = FORMACION ACADEMICA = ESTUDIOS REALIZADOS
class FormacionAcademica(ModeloBase):
    def directory_path(instance, filename):
        return f'empleado/{instance.empleado.ci}/DOC/FORMACION/{filename}'
    
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT,related_name="formacionacademica")
    nivel_academico = models.ForeignKey(
        RefDet,
        verbose_name="Nivel Académico",
        on_delete=models.RESTRICT,
        related_name="nivel_academico_antecedente_academico",
    )
    institucion = models.ForeignKey(Institucion, on_delete=models.RESTRICT, related_name="institucion_antecedente_academico")
    titulo_obtenido = models.ForeignKey(RefDet, on_delete=models.RESTRICT, related_name="titulo_obtenido_antecedente_academico")
    denominacion_carrera = models.CharField(max_length=150, verbose_name="Carrera", null=True, blank=True)
    anho_graduacion = models.IntegerField(verbose_name="Año Graduación", null=True, blank=True)
    archivo_pdf = models.FileField(
        upload_to=directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",null=True, blank=True
    )
    def __str__(self):
        if self.empleado:
            return f"{self.titulo_obtenido} ({self.empleado.nombre} {self.empleado.apellido})"
        return self.titulo

    def toJSON(self):
        item = model_to_dict(self)
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if field.name == 'archivo_pdf':
                # Mostrar solo ícono si hay archivo
                 item['archivo_pdf_url'] = value.url if value else None
                 item[field.name] = "PDF" if value else None
            elif hasattr(value, 'url'):
                item[field.name] = value.url if value else None
            elif hasattr(value, 'name'):
                item[field.name] = value.name if value else None
        item['empleado'] = self.empleado.full_name if self.empleado else None #Empleado nombre completo
        item['institucion_denominacion'] = self.institucion.denominacion if self.institucion else None
        item['nivel_academico_denominacion'] = self.nivel_academico.denominacion if self.nivel_academico else None
        item['titulo_obtenido_denominacion'] = self.titulo_obtenido.denominacion if self.titulo_obtenido else None
        item['denominacion_carrera'] = self.denominacion_carrera if self.denominacion_carrera else None
        # Formatear fecha de graduación
        item['anho_graduacion'] = self.anho_graduacion if self.anho_graduacion else None
        
        return item
    
    class Meta:
        db_table = "rh_formacion_academica"
        verbose_name = "Formación Académica"
        verbose_name_plural = "Formaciones Académicas"
        permissions = [('view_formacionacademica_self', 'Puede ver su propia formación académica'),
                       ('add_formacionacademica_self', 'Puede agregar su propia formación académica'),
                       ('change_formacionacademica_self', 'Puede modificar su propia formación académica'),
                       ('delete_formacionacademica_self', 'Puede eliminar su propia formación académica'),            
                      ]


# CURSOS REALIZADOS = CAPACITACION
class Capacitacion(ModeloBase):
    def directory_path(instance, filename):
        return f'empleado/{instance.empleado.ci}/DOC/CAPACITACION/{filename}'
    
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT,related_name='capacitacion')

    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.RESTRICT,
        related_name="institucion_capacitacion_realizado",
        verbose_name="Institución"
    )
    nombre_capacitacion = models.CharField(
        max_length=150,
        verbose_name="Nombre del Curso"
    )
    tipo_certificacion = models.ForeignKey(
        RefDet,
        on_delete=models.RESTRICT,
        related_name="tipo_certificacion_capacitacion",
        verbose_name="Tipo de Certificación",  # Ej: Participación, Aprobación, Diplomado
        null=True,
        blank=True
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio",
        null=True,
        blank=True
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha de Finalización",
        null=True,
        blank=True
    )
    archivo_pdf = models.FileField(
        upload_to= directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF"
    )
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones"
    )    

    class Meta:
        db_table = "rh_capacitacion"
        verbose_name = "Capacitacion Realizada"
        verbose_name_plural = "Capacitaciones Realizadas"
        ordering = ["-fecha_fin"]
        permissions = [('view_capacitacion_self', 'Puede ver su propia capacitación realizada'),
                       ('add_capacitacion_self', 'Puede agregar su propia capacitación realizada'),
                       ('change_capacitacion_self', 'Puede modificar su propia capacitación realizada'),
                       ('delete_capacitacion_self', 'Puede eliminar su propia capacitación realizada'),            
                      ]

    @property    
    def duracion_dias(self):
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days
        return None
    
    def __str__(self):
        return f"{self.empleado} - {self.nombre_capacitacion}"
    
    def toJSON(self):
        item = model_to_dict(self)
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if field.name == 'archivo_pdf':
                item['archivo_pdf_url'] = value.url if value else None
                item[field.name] = "PDF" if value else None
            elif hasattr(value, 'url'):
                item[field.name] = value.url if value else None
            elif hasattr(value, 'name'):
                item[field.name] = value.name if value else None

        # Campos relacionados con denominación
        item['institucion_denominacion'] = self.institucion.denominacion if self.institucion else None
        item['tipo_certificacion_denominacion'] = self.tipo_certificacion.denominacion if self.tipo_certificacion else None
        item['empleado_ci'] = self.empleado.ci if self.empleado else None
        item['empleado'] = self.empleado.full_name if self.empleado else None #Empleado nombre completo

        # Fechas formateadas
        item['fecha_inicio'] = self.fecha_inicio.strftime('%d/%m/%Y') if self.fecha_inicio else None
        item['fecha_fin'] = self.fecha_fin.strftime('%d/%m/%Y') if self.fecha_fin else None

        return item

class ExperienciaLaboral(ModeloBase):
    def directory_path(instance, filename):
        return f'empleado/{instance.empleado.ci}/DOC/LABORALS/{filename}'
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT,related_name="experiencialaboral")
    institucion = models.ForeignKey(Institucion, on_delete=models.RESTRICT, related_name="institucion_experiencia_profesional")
    cargo = models.ForeignKey(RefDet, on_delete=models.RESTRICT, related_name="cargo_experiencia_profesional")
    fecha_desde = models.DateField(verbose_name="Fecha Desde")
    fecha_hasta = models.DateField(verbose_name="Fecha Hasta", null=True, blank=True)
    motivo_retiro = models.CharField(max_length=255, verbose_name="Motivo Retiro", null=True, blank=True)
    archivo_pdf = models.FileField(
        upload_to=directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF"
    )

    def toJSON(self):
        item = model_to_dict(self, exclude=['archivo_pdf'])
        
        # Archivo PDF
        item['archivo_pdf_url'] = self.archivo_pdf.url if self.archivo_pdf else None
        item['archivo_pdf'] = "PDF" if self.archivo_pdf else None

        # Relaciones
        item['institucion_denominacion'] = self.institucion.denominacion if self.institucion else None
        item['cargo_denominacion'] = self.cargo.denominacion if self.cargo else None
        item['empleado_ci'] = self.empleado.ci if self.empleado else None
        item['empleado'] = self.empleado.full_name if self.empleado else None #Empleado nombre completo

        # Fechas formateadas
        item['fecha_desde'] = self.fecha_desde.strftime('%d/%m/%Y') if self.fecha_desde else None
        item['fecha_hasta'] = self.fecha_hasta.strftime('%d/%m/%Y') if self.fecha_hasta else None

        return item

    
    class Meta:
        db_table = "rh_experiencia_laboral"
        verbose_name = "Experiencia Laboral"
        verbose_name_plural = "Experiencias Laborales"
        permissions = [('view_experiencialaboral_self', 'Puede ver su propia experiencia laboral'),
                       ('add_experiencialaboral_self', 'Puede agregar su propia experiencia laboral'),
                       ('change_experiencialaboral_self', 'Puede modificar su propia experiencia laboral'),
                       ('delete_experiencialaboral_self', 'Puede eliminar su propia experiencia laboral'),
                      ]

# DOCUMENTOS COMPLEMENTARIOS DEL EMPLEADO = OTROS DOCUMENTOS

class DocumentoComplementario(ModeloBase):
    def directory_path(instance, filename):
        return f'empleado/{instance.empleado.ci}/DOC/OTROS/{filename}'
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    tipo_documento = models.ForeignKey(
        RefDet,
        verbose_name="Tipo Documento",
        db_column="tipo_documento",
        on_delete=models.RESTRICT,
        related_name="tipo_documento_empleado",
    )
    descripcion = models.CharField(max_length=255, verbose_name="Descripción", null=True, blank=True)
    archivo_pdf = models.FileField(
        upload_to=directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF"
    )
    estado_documento_empleado = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        verbose_name="Estado del Documento",
        db_column="estado_documento_empleado",
        on_delete=models.RESTRICT,
        related_name="estado_documento_empleado",
        default="S", # Activo
    )

    def toJSON(self):
        item = model_to_dict(self, exclude=['archivo_pdf'])
        # Empleado 
        item['empleado_ci'] = self.empleado.ci if self.empleado else None
        item['empleado'] = self.empleado.full_name if self.empleado else None #Empleado nombre completo

        # Archivo PDF
        item['archivo_pdf_url'] = self.archivo_pdf.url if self.archivo_pdf else None
        item['archivo_pdf'] = "PDF" if self.archivo_pdf else None

        # Relaciones
        item['tipo_documento_denominacion'] = self.tipo_documento.denominacion if self.tipo_documento else None
        item['estado_documento_denominacion'] = self.estado_documento_empleado.descripcion if self.estado_documento_empleado else None

        return item

    def filename(self):
        return os.path.basename(self.archivo.name)
    
    @property
    def ruta_completa(self):
        if self.archivo_pdf:
            return self.archivo_pdf.path  # ruta absoluta en el sistema de archivos
        return None

    class Meta:
        db_table = "rh_documento_complementario"
        verbose_name = "Documento Complementario"
        verbose_name_plural = "Documentos Complementarios"
        permissions = [('view_documentocomplementario_self', 'Puede ver sus propios documentos complementarios'),
                       ('add_documentocomplementario_self', 'Puede agregar sus propios documentos complementarios'),
                       ('change_documentocomplementario_self', 'Puede modificar sus propios documentos complementarios'),
                       ('delete_documentocomplementario_self', 'Puede eliminar sus propios documentos complementarios'),
                      ]

# HISTORICO DISCIPLINARIO = REGISTRO DISCIPLINARIO = ANTECEDENTES DISCIPLINARIOS
class HistoricoDisciplinario(ModeloBase):
    def directory_path(instance, filename):
        return f'empleado/{instance.empleado.ci}/DOC/DISCIPLINARIO/{filename}'
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)

    tipo_falta = models.ForeignKey(
        RefDet,
        verbose_name="Tipo de Falta",
        on_delete=models.RESTRICT,
        related_name="tipo_falta_historico",
        help_text="Ej: Falta Leve, Falta Grave, Falta Muy Grave",
        null=True,
    )
    tipo_sancion = models.ForeignKey(
        RefDet,
        verbose_name="Tipo de Sanción",
        on_delete=models.RESTRICT,
        related_name="tipo_sancion_historico",
        help_text="Ej: Amonestación Verbal, Amonestación Escrita, Suspensión, Despido",
        null=True,
    )
    tipo_documento = models.ForeignKey(
        RefDet,
        verbose_name="Tipo de Documento",
        on_delete=models.RESTRICT,
        related_name="tipo_documento_historico",
        help_text="Ej: Acta, Resolución, Informe, Notificación, Carta Amonestación"
    )

    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción",
        null=True,
        blank=True,
        help_text="Detalle del hecho o resolución disciplinaria"
    )

    fecha_emision = models.DateField(
        verbose_name="Fecha de Emisión",
        null=True,
        blank=True
    )

    institucion_emisora = models.CharField(
        max_length=150,
        verbose_name="Institución Emisora",
        null=True,
        blank=True
    )

    archivo_pdf = models.FileField(
        upload_to=directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Documento PDF",null=True, blank=True
    )

    estado_documento = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        verbose_name="Estado del Documento",
        db_column="estado_documento",
        on_delete=models.RESTRICT,
        related_name="estado_documento_historico",
        default="S"
    )

    def toJSON(self):
        item = model_to_dict(self, exclude=['archivo_pdf'])
        # Empleado 
        item['empleado_ci'] = self.empleado.ci if self.empleado else None
        item['empleado'] = self.empleado.full_name if self.empleado else None #Empleado nombre completo

        # Archivo PDF
        item['archivo_pdf_url'] = self.archivo_pdf.url if self.archivo_pdf else None
        item['archivo_pdf'] = "PDF" if self.archivo_pdf else None

        # Relaciones
        item['tipo_falta_denominacion'] = self.tipo_falta.denominacion if self.tipo_falta else None
        item['tipo_sancion_denominacion'] = self.tipo_sancion.denominacion if self.tipo_sancion else None
        item['tipo_documento_denominacion'] = self.tipo_documento.denominacion if self.tipo_documento else None
        item['estado_documento_denominacion'] = self.estado_documento.denominacion if self.estado_documento else None

        # Fecha formateada
        item['fecha_emision'] = self.fecha_emision.strftime('%d/%m/%Y') if self.fecha_emision else None

        return item

    def filename(self):
        return os.path.basename(self.archivo_pdf.name)

    @property
    def ruta_completa(self):
        if self.archivo_pdf:
            return self.archivo_pdf.path
        return None

    class Meta:
        db_table = "rh_historico_disciplinario"
        verbose_name = "Histórico Disciplinario"
        verbose_name_plural = "Históricos Disciplinarios"
        ordering = ["-fecha_emision"]
        permissions = [('view_historicodisciplinario_self', 'Puede ver su propio histórico disciplinario'),
                       ('add_historicodisciplinario_self', 'Puede agregar su propio histórico disciplinario'),
                       ('change_historicodisciplinario_self', 'Puede modificar su propio histórico disciplinario'),
                       ('delete_historicodisciplinario_self', 'Puede eliminar su propio histórico disciplinario'),            
                      ]
