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
    profesor = models.CharField(max_length=100, blank=True)
    
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
