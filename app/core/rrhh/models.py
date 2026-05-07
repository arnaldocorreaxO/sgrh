import os
from datetime import date

# 1. Librerías de Terceros
from dateutil.relativedelta import relativedelta

# 2. Django Core (Base, Modelos y Validadores)
from django.core.validators import FileExtensionValidator, MinLengthValidator
from django.db import models
from django.db.models import (
    Case,
    ExpressionWrapper,
    Exists,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Q,
    Value,
    When,
)
from django.forms import model_to_dict
from django.utils import timezone

# 3. Aplicaciones Locales (Core, Base y Utils)
from core.models import ModeloBase
from core.user.models import User
from core.utils import UploadToPath
from core.base.choices import *
from core.base.models import Barrio, Ciudad, Moneda, Pais, RefDet, Sucursal
from core.base.utils import calculate_age, calculate_age_detailed


# MANAGERS Y QUERYSETS PERSONALIZADOS
# Para que pueda funcionar .search sobre un queryset filtrado
class EmpleadoQuerySet(models.QuerySet):
    def para_usuario(self, usuario):
        # 1. Superusuario o Admin Global
        if (
            usuario.is_superuser
            or usuario.groups.filter(name="ADMIN_RRHH_GLOBAL").exists()
        ):
            return self.all()

        # 2. Obtener el perfil del consultor
        try:
            empleado_consultor = usuario.empleado
        except AttributeError:
            return self.none()

        # 3. Admin de Sucursal
        if usuario.groups.filter(name="ADMIN_RRHH_SUCURSAL").exists():
            return self.filter(sucursal=empleado_consultor.sucursal)

        # 4. Caso base: Solo a sí mismo
        return self.filter(id=empleado_consultor.id)

    def search(self, term, user, limit=10):
        # 1. Obtenemos el QuerySet base ya filtrado por permisos
        qs = self.para_usuario(user)

        # 2. Limpiamos el término y lo dividimos en palabras
        term_str = str(term).strip() if term else ""
        if not term_str:
            return qs[:limit] if limit else qs

        words = term_str.split()

        # 3. Aplicamos un filtro por cada palabra (Lógica Fuzzy)
        for word in words:
            qs = qs.filter(
                models.Q(nombre__icontains=word)
                | models.Q(apellido__icontains=word)
                | models.Q(ci__icontains=word)
                | models.Q(legajo__icontains=word)
            )

        # 4. Retornamos con el límite aplicado
        # Usamos distinct() por seguridad si hay relaciones complejas
        return qs.distinct()[:limit] if limit else qs.distinct()


class EmpleadoManager(models.Manager):
    def get_queryset(self):
        return EmpleadoQuerySet(self.model, using=self._db)

    # Mapeamos los métodos del manager al queryset para que funcionen desde Empleado.objects...
    def para_usuario(self, usuario):
        return self.get_queryset().para_usuario(usuario)

    def search(self, term, user, limit=10):
        return self.get_queryset().search(term, user, limit)


# INSTITUCION
class Institucion(ModeloBase):
    codigo = models.CharField(max_length=255, unique=True)
    denominacion = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=100)
    tipo_institucion = models.ForeignKey(
        RefDet,
        on_delete=models.RESTRICT,
        related_name="tipo_institucion_institucion",
        null=True,
        blank=True,
    )
    tipo_funcion = models.ForeignKey(
        RefDet,
        on_delete=models.RESTRICT,
        related_name="tipo_funcion_institucion",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.denominacion} - {self.abreviatura}"

    def search(term, limit=10):
        term_str = str(term).strip() if term else ""

        if not term_str:
            return Institucion.objects.none()

        words = term_str.split()
        queryset = Institucion.objects.only("id", "denominacion", "abreviatura")

        for word in words:
            queryset = queryset.filter(
                models.Q(denominacion__icontains=word)
                | models.Q(abreviatura__icontains=word)
            )

        return queryset.order_by("denominacion")[:limit]

    def toJSON(self):
        item = model_to_dict(self)
        item["tipo_institucion__denominacion"] = (
            self.tipo_institucion.denominacion if self.tipo_institucion else None
        )
        item["tipo_funcion__denominacion"] = (
            self.tipo_funcion.denominacion if self.tipo_funcion else None
        )
        return item

    class Meta:
        db_table = "rh_institucion"
        verbose_name = "001 - Institución"
        verbose_name_plural = "001 -Instituciones"


# Relacion Sucursal con Institucion
class SucursalInstitucion(ModeloBase):
    institucion = models.ForeignKey(Institucion, on_delete=models.RESTRICT)
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.RESTRICT, null=True, blank=True
    )
    codigo = models.CharField(max_length=255, unique=True)
    denominacion = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=100)

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "rh_sucursal_institucion"
        verbose_name = "002 - Sucursal Institución"
        verbose_name_plural = "002 - Sucursales Institución"


# DEPENDENCIA = DEPARTAMENTO, AREA, SECCION
class Dependencia(ModeloBase):
    sucursal_institucion = models.ForeignKey(
        SucursalInstitucion, on_delete=models.RESTRICT, null=True, blank=True
    )
    codigo = models.CharField(max_length=255, unique=True)
    denominacion = models.CharField(max_length=255)
    dependencia_padre = models.ForeignKey(
        "self", on_delete=models.RESTRICT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.codigo} - {self.denominacion} - {self.sucursal_institucion.denominacion}"

    @classmethod
    def search(cls, term, padre_id=None, limit=20):
        # Usamos icontains para búsqueda insensible a mayúsculas
        qs = cls.objects.filter(
            models.Q(codigo__icontains=term) | models.Q(denominacion__icontains=term)
        )
        # Si se pasa un padre_id, filtramos las hijas
        if padre_id:
            qs = qs.filter(dependencia_padre_id=padre_id)

        return qs.order_by("denominacion")[:limit]

    class Meta:
        db_table = "rh_dependencia"
        verbose_name = "003 - Dependencia"
        verbose_name_plural = "003 - Dependencias"
        ordering = ["id"]


# CATEGORIA SALARIAL
class CategoriaSalarial(ModeloBase):
    codigo = models.CharField(max_length=4, unique=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.RESTRICT)
    denominacion = models.CharField(max_length=150, verbose_name="Denominación")

    def __str__(self):
        return f"{self.codigo}"

    class Meta:
        db_table = "rh_categoria_salarial"
        verbose_name = "010 - Categoría Salarial"
        verbose_name_plural = "010 - Categorías Salariales"
        ordering = ["id"]


class CategoriaSalarialVigencia(ModeloBase):
    categoria = models.ForeignKey(
        CategoriaSalarial, on_delete=models.CASCADE, related_name="vigencias"
    )
    fecha_vigencia = models.DateField(
        default=timezone.now, verbose_name="Fecha de Vigencia"
    )
    sueldo_basico = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.categoria.codigo} - {self.fecha_vigencia} - {self.sueldo_basico}"

    class Meta:
        db_table = "rh_categoria_salarial_vigencia"
        verbose_name = "011 - Vigencia de Categoría Salarial"
        verbose_name_plural = "011 - Vigencias de Categorías Salariales"
        ordering = ["-fecha_vigencia", "-sueldo_basico"]
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
        ordering = ["id"]


class MatrizSalarial(ModeloBase):
    nivel = models.ForeignKey(
        Nivel, on_delete=models.RESTRICT, related_name="matriz_nivel"
    )
    categoria = models.ForeignKey(
        CategoriaSalarial, on_delete=models.RESTRICT, related_name="matriz_categoria"
    )
    denominacion = models.CharField(
        max_length=150, verbose_name="Denominación", null=True
    )

    def __str__(self):
        return f"{self.categoria} -{self.denominacion}"

    class Meta:
        db_table = "rh_matriz_salarial"
        unique_together = ("nivel", "categoria", "denominacion")
        verbose_name = "021 - Matriz Salarial"
        verbose_name_plural = "021 - Matrices Salariales"
        ordering = ["-categoria__vigencias__sueldo_basico"]


class CargoPuesto(ModeloBase):
    matriz_salarial = models.ForeignKey(
        MatrizSalarial,
        on_delete=models.RESTRICT,
        related_name="matriz_salarial",
        null=True,
        blank=True,
    )
    denominacion = models.CharField(max_length=150, verbose_name="Denominación")

    def __str__(self):
        return f"{self.denominacion} - {self.matriz_salarial.categoria if self.matriz_salarial else ''}"

    class Meta:
        db_table = "rh_cargo_puesto"
        verbose_name = "022 - Cargo Puesto"
        verbose_name_plural = "022 - Cargos Puestos"
        ordering = ["id"]


# EMPLEADO
class Empleado(ModeloBase):
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.RESTRICT
    )
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    legajo = models.CharField(
        verbose_name="Legajo",
        max_length=4,
        validators=[MinLengthValidator(4)],
        null=True,
        blank=True,
    )
    ci = models.BigIntegerField(verbose_name="CI", unique=True)
    fecha_vencimiento_ci = models.DateField(
        verbose_name="Fecha Vencimiento CI", null=True, blank=True
    )
    archivo_pdf_ci = models.FileField(
        upload_to=UploadToPath("CI"),
        verbose_name="Archivo Adjunto CI",
        null=True,
        blank=True,
    )
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
    ciudad = models.ForeignKey(Ciudad, verbose_name="Ciudad", on_delete=models.RESTRICT)
    barrio = models.ForeignKey(
        Barrio, verbose_name="Barrio", on_delete=models.RESTRICT, null=True, blank=True
    )
    direccion = models.CharField(
        verbose_name="Dirección", max_length=100, null=True, blank=True
    )
    telefono = models.CharField(
        verbose_name="Teléfono", max_length=20, null=True, blank=True
    )
    celular = models.CharField(verbose_name="Celular", max_length=20)
    email = models.CharField(max_length=50, verbose_name="Email")
    fecha_nacimiento = models.DateField(verbose_name="Fecha Nacimiento", null=True)
    sexo = models.ForeignKey(
        RefDet,
        verbose_name="Sexo",
        on_delete=models.RESTRICT,
        related_name="sexo_empleado",
    )
    estado_civil = models.ForeignKey(
        RefDet,
        verbose_name="Estado Civil",
        on_delete=models.RESTRICT,
        related_name="estado_civil_empleado",
    )
    tipo_sanguineo = models.ForeignKey(
        RefDet,
        verbose_name="Tipo Sanguíneo",
        on_delete=models.RESTRICT,
        related_name="tipo_sanguineo_empleado",
        null=True,
        blank=True,
    )
    fecha_ingreso = models.DateField(
        verbose_name="Fecha Ingreso", null=True, blank=True
    )

    archivo_pdf_ingreso = models.FileField(
        upload_to=UploadToPath("INGRESO"),
        verbose_name="Resolución Ingreso",
        null=True,
        blank=True,
    )
    fecha_egreso = models.DateField(verbose_name="Fecha Egreso", null=True, blank=True)

    archivo_pdf_egreso = models.FileField(
        upload_to=UploadToPath("EGRESO"),
        verbose_name="Resolución Egreso",
        null=True,
        blank=True,
    )

    # El metodo search está en el EmpleadoQuerySet del EmpleadoManager
    objects = EmpleadoManager()  # Asignamos el manager personalizado

    def __str__(self):
        return self.nombre_apellido

    @property
    def nombre_apellido(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_apellido_legajo(self):
        return f"{self.nombre} {self.apellido} - Legajo: {self.legajo if self.legajo else 'N/A'}"

    def get_ultimo_cargo(self):
        # Ordenamos por fecha_inicio descendente (-) y tomamos el primero
        return self.empleado_posicion.all().order_by("-fecha_inicio").first()

    def posicion_actual(self):
        # Buscamos en la relación inversa 'empleado_posicion' definida en ForeignKey
        return self.empleado_posicion.filter(cargo_puesto_actual=True)

    @property
    def denominacion_cargo_actual(self):
        # Buscamos en la relación inversa 'empleado_posicion' definida en tu ForeignKey
        posicion = self.empleado_posicion.order_by("-fecha_inicio").first()
        if posicion:
            # Retorna la denominación del cargo (tipo_movimiento o cargo según tu lógica)
            return posicion.dependencia_posicion.posicion.denominacion
        return "Cargo"  # Valor por defecto si no hay ninguno activo

    @property
    def denominacion_dependencia_actual(self):
        # Buscamos en la relación inversa 'empleado_posicion' definida en tu ForeignKey
        posicion = self.empleado_posicion.order_by("-fecha_inicio").first()
        if posicion:
            # Retorna la denominación del cargo (tipo_movimiento o cargo según tu lógica)
            return posicion.dependencia_posicion.dependencia.denominacion
        return "Dependencia"  # Valor por defecto si no hay ninguno activo

    @property
    def denominacion_sede_actual(self):
        # Buscamos en la relación inversa 'empleado_posicion' definida en tu ForeignKey
        posicion = self.empleado_posicion.order_by("-fecha_inicio").first()
        if posicion:
            # Retorna la denominación del cargo (tipo_movimiento o cargo según tu lógica)
            return (
                posicion.dependencia_posicion.dependencia.sucursal_institucion.denominacion
            )
        return "Sede"  # Valor por defecto si no hay ninguno activo

    def get_edad(self):
        return calculate_age(self.fecha_nacimiento)

    def get_antiguedad(self):
        if self.fecha_ingreso:
            years, months, days = calculate_age_detailed(self.fecha_ingreso)

            parts = []
            if years > 0:
                parts.append(f"{years} año" if years == 1 else f"{years} años")
            if months > 0:
                parts.append(f"{months} mes" if months == 1 else f"{months} meses")
            if days > 0:
                parts.append(f"{days} día" if days == 1 else f"{days} días")

            if not parts:
                return "0 días"

            # Lógica para unir con comas y el último con una "y"
            if len(parts) > 1:
                resultado = ", ".join(parts[:-1]) + " y " + parts[-1]
            else:
                resultado = parts[0]

            return resultado

        return None

    # 1. FUENTE ÚNICA DE VERDAD: Si cambias esto, cambia en todo el sistema
    PROGRESO_CONFIG = [
        {"nombre": "Foto Tipo Carnet", "campo": "usuario__image", "tipo": "null"},
        {"nombre": "Cédula de Identidad (CI)", "campo": "ci", "tipo": "null"},
        {"nombre": "PDF Cédula", "campo": "archivo_pdf_ci", "tipo": "empty"},
        {"nombre": "PDF Res. Ingreso", "campo": "archivo_pdf_ingreso", "tipo": "empty"},
        {"nombre": "Tipo Sanguíneo", "campo": "tipo_sanguineo", "tipo": "null"},
        {
            "nombre": "Formación Académica",
            "campo": "formacion_academica",
            "tipo": "rel",
        },
        {"nombre": "Capacitaciones", "campo": "capacitacion", "tipo": "rel"},
        {
            "nombre": "Experiencia Laboral",
            "campo": "experiencia_laboral",
            "tipo": "rel",
        },
    ]

    @property
    def progreso_detalle(self):
        completos = 0
        faltantes = []
        total = len(self.PROGRESO_CONFIG)

        for item in self.PROGRESO_CONFIG:
            # Lógica dinámica para validar cada campo en Python
            es_valido = False
            attr_path = item["campo"].split("__")

            # Obtener el valor del campo (incluso si es relación como usuario__image)
            obj = self
            for part in attr_path:
                obj = getattr(obj, part, None) if obj else None

            if item["tipo"] == "null":
                es_valido = bool(obj)
            elif item["tipo"] == "empty":
                es_valido = bool(obj and str(obj).strip() != "")
            elif item["tipo"] == "rel":
                # Accedemos a la relación de forma segura
                rel = getattr(self, item["campo"], None)
                # Verificamos si existe el manager y si tiene registros
                es_valido = rel.exists() if rel and hasattr(rel, "exists") else False

            if es_valido:
                completos += 1
            else:
                faltantes.append(item["nombre"])

        porcentaje = int((completos / total) * 100)
        color = (
            "success"
            if porcentaje == 100
            else "warning" if porcentaje > 0 else "danger"
        )
        mensaje = (
            "Perfil Completo"
            if porcentaje == 100
            else (
                f"Incompleto (Faltan {len(faltantes)})"
                if porcentaje > 0
                else "Perfil Vacío"
            )
        )

        return {
            "color": color,
            "mensaje": mensaje,
            "faltantes": faltantes,
            "porcentaje": porcentaje,
        }

    @staticmethod
    def get_orden_progreso_query():

        query_sumatoria = Value(0)
        config = Empleado.PROGRESO_CONFIG

        for item in config:
            campo = item["campo"]
            tipo = item["tipo"]

            if tipo == "rel":
                # Asegúrate de importar los modelos dentro de la función

                modelos = {
                    "formacion_academica": FormacionAcademica,
                    "capacitacion": Capacitacion,
                    "experiencia_laboral": ExperienciaLaboral,
                }
                modelo = modelos.get(campo)
                if modelo:
                    # Usamos filter(empleado=OuterRef('pk')) o empleado_id
                    condicion = Exists(
                        modelo.objects.filter(empleado_id=OuterRef("pk"))
                    )
                else:
                    condicion = Q(pk__isnull=True)

            elif campo == "ci":
                # Para evitar el error "expected a number", solo verificamos que no sea nulo
                condicion = Q(ci__isnull=False)

            elif "archivo" in campo or "image" in campo:
                # Para archivos, Python mira si hay nombre, SQL mira si no es nulo y no es vacío
                condicion = Q(**{f"{campo}__isnull": False}) & ~Q(**{f"{campo}": ""})

            elif tipo == "null":
                condicion = Q(**{f"{campo}__isnull": False})

            else:  # tipo == "empty"
                condicion = Q(**{f"{campo}__isnull": False}) & ~Q(**{f"{campo}": ""})

            query_sumatoria = query_sumatoria + Case(
                When(condicion, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )

        return ExpressionWrapper(
            (query_sumatoria * 100.0) / len(config),
            output_field=FloatField(),
        )

    def toJSON(self):
        # 1. Convertimos el modelo a diccionario
        item = model_to_dict(self)

        item["legajo"] = self.legajo if self.legajo else "N/A"

        # 2. Propiedades calculadas y personalizadas
        item["nombre_apellido"] = self.nombre_apellido
        item["nombre_apellido_legajo"] = self.nombre_apellido_legajo

        item["antiguedad"] = self.get_antiguedad()

        # 3. Procesar Archivos (PDF e Imagen)
        item["archivo_pdf_ci"] = self.archivo_pdf_ci.url if self.archivo_pdf_ci else ""
        item["archivo_pdf_ingreso"] = (
            self.archivo_pdf_ingreso.url if self.archivo_pdf_ingreso else ""
        )
        item["archivo_pdf_egreso"] = (
            self.archivo_pdf_egreso.url if self.archivo_pdf_egreso else ""
        )

        # Imagen desde el usuario relacionado
        if self.usuario and self.usuario.image:
            item["image"] = self.usuario.image.url
        else:
            item["image"] = "/static/img/empty.png"

        # 4. Formatear Fechas para que no den error de serialización
        item["fecha_nacimiento"] = (
            self.fecha_nacimiento.strftime("%d/%m/%Y") if self.fecha_nacimiento else ""
        )
        item["fecha_vencimiento_ci"] = (
            self.fecha_vencimiento_ci.strftime("%d/%m/%Y")
            if self.fecha_vencimiento_ci
            else ""
        )
        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        # 5. Denominaciones de ForeignKeys (Clave para Reportes y Tablas)
        item["sucursal__cod"] = self.sucursal.cod if self.sucursal else ""
        item["sucursal__denominacion"] = (
            self.sucursal.denominacion if self.sucursal else ""
        )
        item["nacionalidad__denominacion"] = (
            self.nacionalidad.denominacion if self.nacionalidad else ""
        )
        item["ciudad__denominacion"] = self.ciudad.denominacion if self.ciudad else ""

        # Campos de RefDet (Sexo, Estado Civil, etc.)
        item["sexo__denominacion"] = self.sexo.denominacion if self.sexo else ""
        item["estado_civil__denominacion"] = (
            self.estado_civil.denominacion if self.estado_civil else ""
        )
        item["tipo_sanguineo__denominacion"] = (
            self.tipo_sanguineo.denominacion if self.tipo_sanguineo else ""
        )

        item["fecha_ingreso"] = (
            self.fecha_ingreso.strftime("%d/%m/%Y") if self.fecha_ingreso else ""
        )
        item["fecha_egreso"] = (
            self.fecha_egreso.strftime("%d/%m/%Y") if self.fecha_egreso else ""
        )
        # EDAD: Enviamos un objeto con el texto y la fecha real para ordenar
        # (Ordenar por fecha de nacimiento es lo mismo que ordenar por edad)
        item["edad"] = {
            "display": self.get_edad(),
            "timestamp": (
                self.fecha_nacimiento.strftime("%d/%m/%Y")
                if self.fecha_nacimiento
                else ""
            ),
        }

        # PROGRESO: Enviamos el porcentaje para que sea el criterio de orden
        progreso_res = self.progreso_detalle
        progreso_sql = getattr(self, "orden_porcentaje", None)

        # DEBUG: Imprime en consola para comparar
        # print(
        #     f"Empleado {self.id}: SQL={progreso_sql} | Python={progreso_res['porcentaje']}"
        # )

        item["progreso_perfil"] = {
            "display": progreso_res,  # Todo el diccionario con color, mensaje, etc.
            "porcentaje": progreso_sql,  # El número 0-100
        }

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
    posicion = models.ForeignKey(CargoPuesto, on_delete=models.RESTRICT)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.posicion} - {self.dependencia}"

    def search(term, limit=10):
        return DependenciaPosicion.objects.filter(
            models.Q(posicion__denominacion__icontains=term)
            | models.Q(dependencia__denominacion__icontains=term)
        )[:limit]

    class Meta:
        db_table = "rh_dependencia_posicion"
        verbose_name = "023 - Cargo/Puesto por Dependencia"
        verbose_name_plural = "023 - Cargos/Puestos por Dependencias"
        ordering = ["id"]


# EMPLEADO POSICION = ASIGNACION DE CARGO PUESTO
class EmpleadoPosicion(ModeloBase):
    legajo = models.CharField(max_length=4)
    empleado = models.ForeignKey(
        Empleado, on_delete=models.RESTRICT, related_name="empleado_posicion"
    )
    dependencia_posicion = models.ForeignKey(
        DependenciaPosicion, on_delete=models.RESTRICT
    )
    categoria_salarial = models.ForeignKey(
        CategoriaSalarial,
        on_delete=models.RESTRICT,
        related_name="categoria_salarial_empleado_posicion",
        null=True,
        blank=True,
    )
    tipo_movimiento = models.ForeignKey(
        RefDet,
        on_delete=models.RESTRICT,
        related_name="tipo_movimiento_empleado_posicion",
    )
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha Fin", null=True, blank=True)
    cargo_puesto_actual = models.BooleanField(
        default=True, verbose_name="Es su Cargo/Puesto Actual?"
    )
    vinculo_laboral = models.ForeignKey(
        RefDet,
        on_delete=models.RESTRICT,
        related_name="vinculo_laboral_empleado_posicion",
    )
    archivo_pdf = models.FileField(
        upload_to=UploadToPath("POSICION"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "rh_empleado_posicion"
        verbose_name = "024 - Asignación de Cargo/Puesto"
        verbose_name_plural = "024 - Asignaciones de Cargos/Puestos"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.empleado} - {self.dependencia_posicion}"

    def toJSON(self):
        item = model_to_dict(self)
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if field.name == "archivo_pdf":
                # Manejo de archivo similar a FormacionAcademica
                item["archivo_pdf_url"] = value.url if value else None
                item[field.name] = "PDF" if value else None
            elif isinstance(field, models.DateField):
                # Formatear fechas para el DataTable (DD/MM/YYYY)
                item[field.name] = value.strftime("%d/%m/%Y") if value else None
            elif hasattr(value, "url"):
                item[field.name] = value.url if value else None
            elif hasattr(value, "name"):
                item[field.name] = value.name if value else None
        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        # Campos personalizados y denominaciones de ForeignKeys
        item["empleado"] = self.empleado.nombre_apellido if self.empleado else None
        item["empleado_nombre_apellido_legajo"] = (
            self.empleado.nombre_apellido_legajo if self.empleado else None
        )
        item["dependencia_posicion__denominacion"] = (
            str(self.dependencia_posicion) if self.dependencia_posicion else None
        )
        item["tipo_movimiento__denominacion"] = (
            self.tipo_movimiento.denominacion if self.tipo_movimiento else None
        )
        item["vinculo_laboral__denominacion"] = (
            self.vinculo_laboral.denominacion if self.vinculo_laboral else None
        )

        # Estado del cargo actual (para mostrar 'Sí' o 'No' en la tabla si fuera necesario)
        item["cargo_puesto_actual_text"] = "Sí" if self.cargo_puesto_actual else "No"

        return item

    def save(self, *args, **kwargs):
        # 1. Si este registro se marca como actual, gestionamos la exclusividad
        if self.cargo_puesto_actual:
            # Deshabilitar cargos anteriores
            EmpleadoPosicion.objects.filter(
                empleado=self.empleado, cargo_puesto_actual=True
            ).exclude(id=self.id).update(cargo_puesto_actual=False)

            # 2. Recuperar la sucursal desde la dependencia_posicion
            # Ajusta 'dependencia.sucursal_institucion_id' según tus nombres exactos de campos
            nueva_sucursal = (
                self.dependencia_posicion.dependencia.sucursal_institucion.sucursal
            )

            if nueva_sucursal:
                # Actualizar sucursal en el Empleado
                self.empleado.sucursal = nueva_sucursal

                # Actualizar sucursal en el Usuario vinculado (si existe)
                if self.empleado.usuario:
                    self.empleado.usuario.sucursal = nueva_sucursal
                    self.empleado.usuario.save(update_fields=["sucursal"])

        # 3. Actualizar siempre el legajo del empleado
        self.empleado.legajo = self.legajo
        # Guardamos los cambios realizados en el empleado (legajo y sucursal)
        self.empleado.save(update_fields=["legajo", "sucursal"])

        super().save(*args, **kwargs)

    def get_antiguedad(self):
        if self.fecha_inicio:
            # timezone.now().date() obtiene la fecha real cada vez que se ejecuta el método
            # sin importar cuánto tiempo lleve encendido el servidor.
            hoy = timezone.now().date()

            fecha_fin = self.fecha_fin if self.fecha_fin else hoy

            # Calculamos la diferencia
            diff = relativedelta(fecha_fin, self.fecha_inicio)

            # Construimos el texto dinámicamente con manejo de singular/plural
            parts = []

            if diff.years > 0:
                # Si diff.years es 1 usa "año", de lo contrario "años"
                label = "año" if diff.years == 1 else "años"
                parts.append(f"{diff.years} {label}")

            if diff.months > 0:
                # Si diff.months es 1 usa "mes", de lo contrario "meses"
                label = "mes" if diff.months == 1 else "meses"
                parts.append(f"{diff.months} {label}")

            if diff.days > 0:
                # Si diff.days es 1 usa "día", de lo contrario "días"
                label = "día" if diff.days == 1 else "días"
                parts.append(f"{diff.days} {label}")

            # Unimos las partes con comas
            resultado = ", ".join(parts) if parts else "0 días"

            if not self.fecha_fin:
                resultado += " (Actualidad)"

            return resultado
        return "Sin fecha de inicio"


# ANTECEDENTES ACADEMICOS = FORMACION ACADEMICA = ESTUDIOS REALIZADOS
class FormacionAcademica(ModeloBase):
    empleado = models.ForeignKey(
        Empleado, on_delete=models.RESTRICT, related_name="formacion_academica"
    )
    nivel_academico = models.ForeignKey(
        RefDet,
        verbose_name="Nivel Académico",
        on_delete=models.RESTRICT,
        related_name="nivel_academico_antecedente_academico",
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.RESTRICT,
        related_name="institucion_antecedente_academico",
    )
    grado_academico = models.ForeignKey(
        RefDet,
        verbose_name="Grado Académico",
        on_delete=models.RESTRICT,
        related_name="grado_academico_antecedente_academico",
        default=0,  # 0 (cero) Valor por defecto del sistema
    )
    denominacion_carrera = models.CharField(
        max_length=150, verbose_name="Carrera", null=True, blank=True
    )
    titulo_obtenido = models.CharField(
        max_length=150, verbose_name="Título Obtenido", null=True, blank=True
    )
    anho_graduacion = models.IntegerField(
        verbose_name="Año Graduación", null=True, blank=True
    )
    archivo_pdf = models.FileField(
        upload_to=UploadToPath("FORMACION"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.empleado:
            return f"{self.titulo_obtenido} ({self.empleado.nombre} {self.empleado.apellido})"
        return self.titulo_obtenido

    def toJSON(self):
        item = model_to_dict(self)
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if field.name == "archivo_pdf":
                # Mostrar solo ícono si hay archivo
                item["archivo_pdf_url"] = value.url if value else None
                item[field.name] = "PDF" if value else None
            elif hasattr(value, "url"):
                item[field.name] = value.url if value else None
            elif hasattr(value, "name"):
                item[field.name] = value.name if value else None
        item["empleado"] = (
            self.empleado.nombre_apellido if self.empleado else None
        )  # Empleado nombre completo
        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        item["institucion__denominacion"] = (
            self.institucion.denominacion if self.institucion else None
        )
        item["nivel_academico__denominacion"] = (
            self.nivel_academico.denominacion if self.nivel_academico else None
        )
        item["grado_academico__denominacion"] = (
            self.grado_academico.denominacion if self.grado_academico else None
        )
        item["titulo_obtenido"] = self.titulo_obtenido if self.titulo_obtenido else None
        item["denominacion_carrera"] = (
            self.denominacion_carrera if self.denominacion_carrera else None
        )
        # Formatear fecha de graduación
        item["anho_graduacion"] = self.anho_graduacion if self.anho_graduacion else None

        return item

    class Meta:
        db_table = "rh_formacion_academica"
        verbose_name = "Formación Académica"
        verbose_name_plural = "Formaciones Académicas"
        ordering = ["-anho_graduacion"]
        permissions = [
            ("view_formacionacademica_self", "Puede ver su propia formación académica"),
            (
                "add_formacionacademica_self",
                "Puede agregar su propia formación académica",
            ),
            (
                "change_formacionacademica_self",
                "Puede modificar su propia formación académica",
            ),
            (
                "delete_formacionacademica_self",
                "Puede eliminar su propia formación académica",
            ),
        ]


# CURSOS REALIZADOS = CAPACITACION
class Capacitacion(ModeloBase):
    empleado = models.ForeignKey(
        Empleado, on_delete=models.RESTRICT, related_name="capacitacion"
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.RESTRICT,
        related_name="institucion_capacitacion_realizado",
        verbose_name="Institución",
    )
    nombre_capacitacion = models.CharField(
        max_length=150, verbose_name="Nombre del Curso"
    )
    tipo_certificacion = models.ForeignKey(
        RefDet,
        on_delete=models.RESTRICT,
        related_name="tipo_certificacion_capacitacion",
        verbose_name="Tipo de Certificación",  # Ej: Participación, Aprobación, Diplomado
        null=True,
        blank=True,
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio", null=True, blank=True
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha de Finalización", null=True, blank=True
    )
    horas_acreditadas = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Horas Acreditadas",
        null=True,
        blank=True,
    )
    archivo_pdf = models.FileField(
        upload_to=UploadToPath("CAPACITACION"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",
    )
    observaciones = models.TextField(
        null=True, blank=True, verbose_name="Observaciones"
    )

    class Meta:
        db_table = "rh_capacitacion"
        verbose_name = "Capacitacion Realizada"
        verbose_name_plural = "Capacitaciones Realizadas"
        ordering = ["-fecha_fin"]
        permissions = [
            ("view_capacitacion_self", "Puede ver su propia capacitación realizada"),
            ("add_capacitacion_self", "Puede agregar su propia capacitación realizada"),
            (
                "change_capacitacion_self",
                "Puede modificar su propia capacitación realizada",
            ),
            (
                "delete_capacitacion_self",
                "Puede eliminar su propia capacitación realizada",
            ),
        ]

    @property
    def duracion_dias(self):
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days
        return None

    def __str__(self):
        return f"{self.nombre_capacitacion}"

    def toJSON(self):
        item = model_to_dict(self)
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if field.name == "archivo_pdf":
                item["archivo_pdf_url"] = value.url if value else None
                item[field.name] = "PDF" if value else None
            elif hasattr(value, "url"):
                item[field.name] = value.url if value else None
            elif hasattr(value, "name"):
                item[field.name] = value.name if value else None
        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        # Campos relacionados con denominación
        item["institucion__denominacion"] = (
            str(self.institucion) if self.institucion else None
        )
        item["tipo_certificacion__denominacion"] = (
            self.tipo_certificacion.denominacion if self.tipo_certificacion else None
        )
        item["empleado__ci"] = self.empleado.ci if self.empleado else None
        item["empleado"] = (
            self.empleado.nombre_apellido if self.empleado else None
        )  # Empleado nombre completo

        # Fechas formateadas
        item["fecha_inicio"] = (
            self.fecha_inicio.strftime("%d/%m/%Y") if self.fecha_inicio else None
        )
        item["fecha_fin"] = (
            self.fecha_fin.strftime("%d/%m/%Y") if self.fecha_fin else None
        )
        item["horas_acreditadas"] = (
            self.horas_acreditadas if self.horas_acreditadas else "No especificado"
        )

        return item


class ExperienciaLaboral(ModeloBase):
    empleado = models.ForeignKey(
        Empleado, on_delete=models.RESTRICT, related_name="experiencia_laboral"
    )
    empresa = models.ForeignKey(
        RefDet,
        db_column="empresa_refdet_id",
        on_delete=models.RESTRICT,
        related_name="empresa_experiencia_laboral",
    )
    cargo = models.ForeignKey(
        RefDet,
        db_column="cargo_refdet_id",
        on_delete=models.RESTRICT,
        related_name="cargo_experiencia_laboral",
    )
    fecha_desde = models.DateField(verbose_name="Fecha Desde")
    fecha_hasta = models.DateField(verbose_name="Fecha Hasta", null=True, blank=True)
    actividades = models.CharField(
        max_length=255, verbose_name="Actividades", null=True, blank=True
    )
    archivo_pdf = models.FileField(
        upload_to=UploadToPath("LABORAL"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",
    )

    class Meta:
        db_table = "rh_experiencia_laboral"
        verbose_name = "Experiencia Laboral"
        verbose_name_plural = "Experiencias Laborales"
        ordering = [F("fecha_hasta").desc(nulls_first=True), "-fecha_desde"]
        permissions = [
            ("view_experiencialaboral_self", "Puede ver su propia experiencia laboral"),
            (
                "add_experiencialaboral_self",
                "Puede agregar su propia experiencia laboral",
            ),
            (
                "change_experiencialaboral_self",
                "Puede modificar su propia experiencia laboral",
            ),
            (
                "delete_experiencialaboral_self",
                "Puede eliminar su propia experiencia laboral",
            ),
        ]

    def toJSON(self):
        item = model_to_dict(self, exclude=["archivo_pdf"])

        # Archivo PDF
        item["archivo_pdf_url"] = self.archivo_pdf.url if self.archivo_pdf else None
        item["archivo_pdf"] = "PDF" if self.archivo_pdf else None

        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        item["empresa__denominacion"] = (
            self.empresa.denominacion if self.empresa else None
        )
        item["cargo__denominacion"] = self.cargo.denominacion if self.cargo else None
        item["empleado__ci"] = self.empleado.ci if self.empleado else None
        item["empleado"] = (
            self.empleado.nombre_apellido if self.empleado else None
        )  # Empleado nombre completo

        # Fechas formateadas
        item["fecha_desde"] = (
            self.fecha_desde.strftime("%d/%m/%Y") if self.fecha_desde else None
        )
        item["fecha_hasta"] = (
            self.fecha_hasta.strftime("%d/%m/%Y") if self.fecha_hasta else None
        )

        return item

    def get_antiguedad(self):
        if self.fecha_desde:
            # timezone.now().date() obtiene la fecha real cada vez que se ejecuta el método
            # sin importar cuánto tiempo lleve encendido el servidor.
            hoy = timezone.now().date()

            fecha_fin = self.fecha_hasta if self.fecha_hasta else hoy

            # Calculamos la diferencia
            diff = relativedelta(fecha_fin, self.fecha_desde)

            # Construimos el texto dinámicamente con manejo de singular/plural
            parts = []

            if diff.years > 0:
                # Si diff.years es 1 usa "año", de lo contrario "años"
                label = "año" if diff.years == 1 else "años"
                parts.append(f"{diff.years} {label}")

            if diff.months > 0:
                # Si diff.months es 1 usa "mes", de lo contrario "meses"
                label = "mes" if diff.months == 1 else "meses"
                parts.append(f"{diff.months} {label}")

            if diff.days > 0:
                # Si diff.days es 1 usa "día", de lo contrario "días"
                label = "día" if diff.days == 1 else "días"
                parts.append(f"{diff.days} {label}")

            # Unimos las partes con comas
            resultado = ", ".join(parts) if parts else "0 días"

            if not self.fecha_hasta:
                resultado += " (Actualidad)"

            return resultado
        return "Sin fecha de inicio"


# DOCUMENTOS COMPLEMENTARIOS DEL EMPLEADO = OTROS DOCUMENTOS
class DocumentoComplementario(ModeloBase):
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    fecha_documento = models.DateField(
        verbose_name="Fecha del Documento", null=True, blank=True, default=timezone.now
    )
    tipo_documento = models.ForeignKey(
        RefDet,
        verbose_name="Tipo Documento",
        db_column="tipo_documento",
        on_delete=models.RESTRICT,
        related_name="tipo_documento_empleado",
    )
    descripcion = models.CharField(
        max_length=255, verbose_name="Descripción", null=True, blank=True
    )
    archivo_pdf = models.FileField(
        upload_to=UploadToPath("OTROS"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Archivo PDF",
    )
    estado_documento_empleado = models.ForeignKey(
        RefDet,
        verbose_name="Estado del Documento",
        db_column="estado_documento_empleado",
        on_delete=models.RESTRICT,
        related_name="estado_documento_empleado",
    )

    class Meta:
        db_table = "rh_documento_complementario"
        verbose_name = "Documento Complementario"
        verbose_name_plural = "Documentos Complementarios"
        permissions = [
            (
                "view_documentocomplementario_self",
                "Puede ver sus propios documentos complementarios",
            ),
            (
                "add_documentocomplementario_self",
                "Puede agregar sus propios documentos complementarios",
            ),
            (
                "change_documentocomplementario_self",
                "Puede modificar sus propios documentos complementarios",
            ),
            (
                "delete_documentocomplementario_self",
                "Puede eliminar sus propios documentos complementarios",
            ),
        ]

    def toJSON(self):
        item = model_to_dict(self, exclude=["archivo_pdf"])
        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        # Empleado
        item["empleado__ci"] = self.empleado.ci if self.empleado else None
        item["empleado"] = (
            self.empleado.nombre_apellido if self.empleado else None
        )  # Empleado nombre completo

        # Fecha formateada
        item["fecha_documento"] = (
            self.fecha_documento.strftime("%d/%m/%Y") if self.fecha_documento else None
        )

        # Archivo PDF
        item["archivo_pdf_url"] = self.archivo_pdf.url if self.archivo_pdf else None
        item["archivo_pdf"] = "PDF" if self.archivo_pdf else None

        # Relaciones
        item["tipo_documento__denominacion"] = (
            self.tipo_documento.denominacion if self.tipo_documento else None
        )
        item["estado_documento__denominacion"] = (
            self.estado_documento_empleado.denominacion
            if self.estado_documento_empleado
            else None
        )
        return item

    def filename(self):
        return os.path.basename(self.archivo.name)

    @property
    def ruta_completa(self):
        if self.archivo_pdf:
            return self.archivo_pdf.path  # ruta absoluta en el sistema de archivos
        return None


# HISTORICO DISCIPLINARIO = REGISTRO DISCIPLINARIO = ANTECEDENTES DISCIPLINARIOS
class HistoricoDisciplinario(ModeloBase):
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
        help_text="Ej: Acta, Resolución, Informe, Notificación, Carta Amonestación",
    )

    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción",
        null=True,
        blank=True,
        help_text="Detalle del hecho o resolución disciplinaria",
    )

    fecha_emision = models.DateField(
        verbose_name="Fecha de Emisión", null=True, blank=True
    )

    institucion_emisora = models.CharField(
        max_length=150, verbose_name="Institución Emisora", null=True, blank=True
    )

    archivo_pdf = models.FileField(
        upload_to=UploadToPath("DISCIPLINARIO"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Documento PDF",
        null=True,
        blank=True,
    )

    estado_documento = models.ForeignKey(
        RefDet,
        verbose_name="Estado del Documento",
        db_column="estado_documento",
        on_delete=models.RESTRICT,
        related_name="estado_documento_historico",
    )

    def toJSON(self):
        item = model_to_dict(self, exclude=["archivo_pdf"])
        # Empleado
        # Relaciones
        # Se usa doble guión '__' para que el nombre en el JSON coincida con el campo del ORM.
        # Esto permite que el ordenamiento de DataTables funcione sin mapeos adicionales.
        item["empleado__ci"] = self.empleado.ci if self.empleado else None
        item["empleado"] = (
            self.empleado.nombre_apellido if self.empleado else None
        )  # Empleado nombre completo

        # Archivo PDF
        item["archivo_pdf_url"] = self.archivo_pdf.url if self.archivo_pdf else None
        item["archivo_pdf"] = "PDF" if self.archivo_pdf else None

        # Relaciones
        item["tipo_falta__denominacion"] = (
            self.tipo_falta.denominacion if self.tipo_falta else None
        )
        item["tipo_sancion__denominacion"] = (
            self.tipo_sancion.denominacion if self.tipo_sancion else None
        )
        item["tipo_documento__denominacion"] = (
            self.tipo_documento.denominacion if self.tipo_documento else None
        )
        item["estado_documento__denominacion"] = (
            self.estado_documento.denominacion if self.estado_documento else None
        )

        # Fecha formateada
        item["fecha_emision"] = (
            self.fecha_emision.strftime("%d/%m/%Y") if self.fecha_emision else None
        )

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
        permissions = [
            (
                "view_historicodisciplinario_self",
                "Puede ver su propio histórico disciplinario",
            ),
            (
                "add_historicodisciplinario_self",
                "Puede agregar su propio histórico disciplinario",
            ),
            (
                "change_historicodisciplinario_self",
                "Puede modificar su propio histórico disciplinario",
            ),
            (
                "delete_historicodisciplinario_self",
                "Puede eliminar su propio histórico disciplinario",
            ),
        ]
