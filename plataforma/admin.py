from django.contrib import admin
from .models import Estudiante, Curso, Mensaje


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'grado', 'numero_matricula']
    search_fields = ['nombre', 'email']
    list_filter = ['grado']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'profesor', 'icono']
    search_fields = ['nombre', 'profesor']


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'asunto', 'fecha_envio', 'leido']
    search_fields = ['nombre', 'asunto']
    list_filter = ['leido', 'fecha_envio']
    readonly_fields = ['fecha_envio']