from django.contrib import admin
from .models import (
    Carrera, Periodo, Materia, PerfilEstudiante,
    Matricula, Calificacion, Tarea, EntregaTarea,
    Certificado, BibliotecaDigital, Mensaje
)

# ===== ESTRUCTURA ACADÉMICA =====
@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'creditos_totales')
    search_fields = ('nombre', 'codigo')

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('activo',)

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'carrera', 'creditos')
    search_fields = ('codigo', 'nombre')
    list_filter = ('carrera',)

@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_matricula', 'carrera', 'activo')
    search_fields = ('numero_matricula', 'cedula')
    list_filter = ('carrera', 'activo')

# ===== ACADÉMICO =====
@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'materia', 'periodo', 'estado', 'nota_final')
    list_filter = ('estado', 'periodo')
    search_fields = ('estudiante__username', 'materia__codigo')

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'tipo', 'valor', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('matricula__estudiante__username',)

# ===== RECURSOS =====
@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('materia', 'titulo', 'fecha_entrega')
    list_filter = ('materia', 'fecha_entrega')
    search_fields = ('titulo',)

@admin.register(EntregaTarea)
class EntregaTareaAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'estudiante', 'estado', 'calificacion')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('estudiante__username', 'tarea__titulo')

@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'tipo', 'carrera', 'fecha_emision')
    list_filter = ('tipo', 'fecha_emision')
    search_fields = ('estudiante__username', 'codigo_verificacion')

@admin.register(BibliotecaDigital)
class BibliotecaDigitalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'acceso_abierto', 'fecha_agregada')
    list_filter = ('acceso_abierto', 'fecha_agregada')
    search_fields = ('titulo', 'autor', 'isbn')

# ===== COMUNICACIÓN =====
@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'asunto', 'fecha_envio', 'leido')
    list_filter = ('leido', 'fecha_envio')
    search_fields = ('nombre', 'email', 'asunto')
