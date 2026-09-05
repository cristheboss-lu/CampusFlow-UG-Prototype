from django.contrib import admin
from .models import (
    Carrera, Periodo, Materia, PerfilEstudiante, PerfilDocente, PerfilUsuario,
    Matricula, Calificacion, Tarea, EntregaTarea,
    Certificado, BibliotecaDigital, Mensaje,
    Planificacion, Parcial, Unidad, ActividadPlanificada
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
    list_display = ('codigo', 'nombre', 'carrera', 'docente', 'creditos')
    search_fields = ('codigo', 'nombre')
    list_filter = ('carrera',)

@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_matricula', 'carrera', 'activo')
    search_fields = ('numero_matricula', 'cedula')
    list_filter = ('carrera', 'activo')

@admin.register(PerfilDocente)
class PerfilDocenteAdmin(admin.ModelAdmin):
    list_display = ('user', 'cedula', 'carrera', 'titulo_academico', 'activo')
    search_fields = ('cedula', 'user__username')
    list_filter = ('carrera', 'activo')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

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


# ===== PLANIFICACIÓN SEMESTRAL =====
class ParcialInline(admin.TabularInline):
    model = Parcial
    extra = 0

class UnidadInline(admin.TabularInline):
    model = Unidad
    extra = 0

class ActividadPlanificadaInline(admin.TabularInline):
    model = ActividadPlanificada
    extra = 0

@admin.register(Planificacion)
class PlanificacionAdmin(admin.ModelAdmin):
    list_display = ('materia', 'periodo', 'docente', 'fecha_actualizacion')
    list_filter = ('periodo', 'materia__carrera')
    search_fields = ('materia__codigo', 'materia__nombre')
    inlines = [ParcialInline]

@admin.register(Parcial)
class ParcialAdmin(admin.ModelAdmin):
    list_display = ('planificacion', 'numero', 'nombre', 'peso_formativa', 'peso_practica', 'peso_examen', 'peso_total')
    list_filter = ('planificacion__periodo',)
    inlines = [UnidadInline]

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ('parcial', 'numero', 'tema')
    search_fields = ('tema',)
    inlines = [ActividadPlanificadaInline]

@admin.register(ActividadPlanificada)
class ActividadPlanificadaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad', 'semana', 'categoria', 'fecha_entrega', 'permite_entrega_tardia')
    list_filter = ('categoria', 'permite_entrega_tardia', 'unidad__parcial__planificacion__periodo')
    search_fields = ('nombre',)
