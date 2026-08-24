from django.db import models

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    grado = models.CharField(max_length=50)
    numero_matricula = models.CharField(max_length=50, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Estudiantes"


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    profesor = models.CharField(max_length=100)
    url_aula = models.URLField()
    descripcion = models.TextField()
    icono = models.CharField(max_length=50, default="📚")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Cursos"


class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.asunto} - {self.nombre}"

    class Meta:
        verbose_name_plural = "Mensajes"
        ordering = ['-fecha_envio']