from django.contrib import admin
from .models import (
    Carrera, Periodo, Materia, PerfilEstudiante, 
    Matricula, Calificacion, Tarea, EntregaTarea,
    Certificado, BibliotecaDigital, Mensaje
)

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
    list_display = ('codigo', 'nombre', 'carrera', 'creditos', 'profesor')
    list_filter = ('carrera',)
    search_fields = ('codigo', 'nombre')

@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_matricula', 'carrera', 'activo')
    list_filter = ('carrera', 'activo')
    search_fields = ('numero_matricula', 'cedula', 'user__username')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'materia', 'periodo', 'estado', 'nota_final')
    list_filter = ('estado', 'periodo')
    search_fields = ('estudiante__username', 'materia__codigo')

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'tipo', 'valor', 'fecha')
    list_filter = ('tipo', 'fecha')

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('materia', 'titulo', 'fecha_asignacion', 'fecha_entrega')
    list_filter = ('materia', 'fecha_entrega')
    search_fields = ('titulo',)

@admin.register(EntregaTarea)
class EntregaTareaAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'estudiante', 'estado', 'calificacion')
    list_filter = ('estado',)
    search_fields = ('estudiante__username',)

@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'carrera', 'tipo', 'fecha_emision')
    list_filter = ('carrera', 'tipo')
    search_fields = ('estudiante__username', 'codigo_verificacion')

@admin.register(BibliotecaDigital)
class BibliotecaDigitalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha_agregada', 'acceso_abierto')
    list_filter = ('acceso_abierto', 'fecha_agregada')
    search_fields = ('titulo', 'autor', 'isbn')

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'asunto', 'fecha_envio', 'leido')
    list_filter = ('leido', 'fecha_envio')
    search_fields = ('nombre', 'email', 'asunto')
    actions = ['marcar_como_leido']
    
    def marcar_como_leido(self, request, queryset):
        queryset.update(leido=True)
    marcar_como_leido.short_description = "Marcar como leído"
