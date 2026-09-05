from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import cloudinary.models

# ===== ESTRUCTURA ACADÉMICA =====
class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    creditos_totales = models.IntegerField(default=120)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Carreras"


class Periodo(models.Model):
    nombre = models.CharField(max_length=20)  # 2026-1, 2026-2
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Período {self.nombre}"
    
    class Meta:
        verbose_name_plural = "Períodos"


class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='materias')
    creditos = models.IntegerField(default=4)
    descripcion = models.TextField(blank=True)
    profesor = models.CharField(max_length=100, blank=True)  # legado: se conserva por datos existentes
    docente = models.ForeignKey(
        'PerfilDocente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materias'
    )
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        verbose_name_plural = "Materias"


class PerfilEstudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_estudiante')
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True)
    numero_matricula = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.numero_matricula}"
    
    class Meta:
        verbose_name_plural = "Perfiles de Estudiante"


class PerfilDocente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_docente')
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='docentes')
    cedula = models.CharField(max_length=20, unique=True)
    titulo_academico = models.CharField(max_length=100, blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.titulo_academico}"

    class Meta:
        verbose_name_plural = "Perfiles de Docente"


class PerfilUsuario(models.Model):
    """
    Perfil ligero que guarda el ROL del usuario (admin/docente/estudiante).
    Es independiente de PerfilEstudiante y PerfilDocente, que guardan datos
    académicos específicos de cada rol. Este solo sirve para saber a qué
    panel debe redirigir el login y qué permisos tiene.
    """
    ROLES = [
        ('admin', 'Administrador / Secretaría'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_usuario')
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_rol_display()}"

    class Meta:
        verbose_name_plural = "Perfiles de Usuario"


# ===== ACADÉMICO =====
class Matricula(models.Model):
    ESTADOS = [
        ('Cursando', 'Cursando'),
        ('Aprobado', 'Aprobado'),
        ('Reprobado', 'Reprobado'),
        ('Retirado', 'Retirado'),
    ]
    
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matriculas')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='matriculas')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='matriculas')
    fecha_matricula = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Cursando')
    nota_final = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    asistencia = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return f"{self.estudiante.get_full_name()} - {self.materia.codigo} ({self.periodo.nombre})"
    
    class Meta:
        verbose_name_plural = "Matrículas"
        unique_together = ('estudiante', 'materia', 'periodo')


class Calificacion(models.Model):
    TIPOS = [
        ('Parcial 1', 'Parcial 1'),
        ('Parcial 2', 'Parcial 2'),
        ('Parcial 3', 'Parcial 3'),
        ('Examen Final', 'Examen Final'),
        ('Trabajo', 'Trabajo'),
    ]
    
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='calificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    valor = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    fecha = models.DateField(auto_now_add=True)
    observacion = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.matricula.estudiante.get_full_name()} - {self.tipo}: {self.valor}"
    
    class Meta:
        verbose_name_plural = "Calificaciones"


# ===== RECURSOS =====
class Tarea(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='tareas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_entrega = models.DateField()
    
    # Almacenar en Cloudinary desde el inicio
    pdf_guia = cloudinary.models.CloudinaryField('guias', null=True, blank=True)
    
    def __str__(self):
        return f"{self.materia.codigo} - {self.titulo}"
    
    class Meta:
        verbose_name_plural = "Tareas"


class EntregaTarea(models.Model):
    ESTADOS = [
        ('Entregado', 'Entregado'),
        ('Calificado', 'Calificado'),
        ('Atrasado', 'Atrasado'),
    ]
    
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='entregas')
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo = cloudinary.models.CloudinaryField('entregas', null=True, blank=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    calificacion = models.FloatField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Entregado')
    observacion = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.estudiante.get_full_name()} - {self.tarea.titulo}"
    
    class Meta:
        verbose_name_plural = "Entregas de Tareas"
        unique_together = ('tarea', 'estudiante')


class Certificado(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificados')
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # "Término", "Técnico", etc
    fecha_emision = models.DateField(auto_now_add=True)
    codigo_verificacion = models.CharField(max_length=20, unique=True)
    qr_code = cloudinary.models.CloudinaryField('qr_codes', null=True, blank=True)
    
    def __str__(self):
        return f"Certificado {self.tipo} - {self.estudiante.get_full_name()}"
    
    class Meta:
        verbose_name_plural = "Certificados"


class BibliotecaDigital(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True, blank=True)
    descripcion = models.TextField()
    pdf = cloudinary.models.CloudinaryField('libros', null=True, blank=True)
    fecha_agregada = models.DateField(auto_now_add=True)
    acceso_abierto = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name_plural = "Biblioteca Digital"


# ===== COMUNICACIÓN =====
class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nombre} - {self.asunto}"
    
    class Meta:
        verbose_name_plural = "Mensajes"


# ===== PLANIFICACIÓN SEMESTRAL =====
class Planificacion(models.Model):
    """
    Planificación de una materia para un período concreto.
    Es el contenedor de los parciales, unidades y actividades del semestre.
    """
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='planificaciones')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='planificaciones')
    docente = models.ForeignKey(
        PerfilDocente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planificaciones'
    )
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.materia.codigo} - {self.periodo.nombre}"

    class Meta:
        verbose_name_plural = "Planificaciones"
        unique_together = ('materia', 'periodo')
        ordering = ['-periodo__fecha_inicio', 'materia__codigo']


class Parcial(models.Model):
    """
    Un parcial de la planificación. Define cuánto pesa cada categoría de
    actividad (formativa / práctica / examen) sobre la nota del parcial.
    Los tres pesos deben sumar 100.
    """
    planificacion = models.ForeignKey(Planificacion, on_delete=models.CASCADE, related_name='parciales')
    numero = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    nombre = models.CharField(max_length=50, blank=True)
    peso_formativa = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_practica = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_examen = models.IntegerField(default=40, validators=[MinValueValidator(0), MaxValueValidator(100)])

    @property
    def peso_total(self):
        return self.peso_formativa + self.peso_practica + self.peso_examen

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.peso_total != 100:
            raise ValidationError(
                f"Los pesos deben sumar 100 (actualmente suman {self.peso_total})."
            )

    def __str__(self):
        return f"{self.planificacion.materia.codigo} - {self.nombre or f'Parcial {self.numero}'}"

    class Meta:
        verbose_name_plural = "Parciales"
        unique_together = ('planificacion', 'numero')
        ordering = ['numero']


class Unidad(models.Model):
    """
    Unidad temática dentro de un parcial. El tema es fijo (lo define la
    planificación); lo editable son las actividades que cuelgan de ella.
    """
    parcial = models.ForeignKey(Parcial, on_delete=models.CASCADE, related_name='unidades')
    numero = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    tema = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"Unidad {self.numero}: {self.tema}"

    class Meta:
        verbose_name_plural = "Unidades"
        unique_together = ('parcial', 'numero')
        ordering = ['numero']


class ActividadPlanificada(models.Model):
    """
    Actividad concreta de una unidad, ubicada en una semana del semestre.
    Su categoría determina contra qué peso del parcial promedia la nota.
    """
    CATEGORIAS = [
        ('formativa', 'Formativa'),
        ('practica', 'Práctica'),
        ('examen', 'Examen'),
    ]

    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='actividades')
    semana = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(24)])
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='formativa')
    archivo = cloudinary.models.CloudinaryField('planificacion', null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField()
    permite_entrega_tardia = models.BooleanField(default=False)
    fecha_limite_tardia = models.DateField(null=True, blank=True)
    penalizacion_tardia = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje que se descuenta a las entregas fuera de plazo."
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_inicio and self.fecha_inicio > self.fecha_entrega:
            raise ValidationError("La fecha de inicio no puede ser posterior a la de entrega.")
        if self.permite_entrega_tardia:
            if not self.fecha_limite_tardia:
                raise ValidationError("Indica la fecha límite para entregas tardías.")
            if self.fecha_limite_tardia < self.fecha_entrega:
                raise ValidationError("La fecha límite tardía debe ser posterior a la de entrega.")

    def acepta_entrega(self, fecha):
        """¿Se puede entregar esta actividad en la fecha dada?"""
        if fecha <= self.fecha_entrega:
            return True
        return bool(self.permite_entrega_tardia and self.fecha_limite_tardia and fecha <= self.fecha_limite_tardia)

    def es_tardia(self, fecha):
        return fecha > self.fecha_entrega

    def __str__(self):
        return f"S{self.semana} - {self.nombre} ({self.get_categoria_display()})"

    class Meta:
        verbose_name_plural = "Actividades Planificadas"
        ordering = ['semana', 'id']
