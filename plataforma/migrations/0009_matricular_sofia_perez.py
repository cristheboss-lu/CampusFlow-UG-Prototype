from datetime import timedelta

from django.db import migrations

# Mismo reparto estándar de 16 semanas / 3 parciales que usa
# _generar_planificacion_estandar en views.py.
_SEMANAS_POR_PARCIAL = [
    (1, range(1, 6)),
    (2, range(6, 11)),
    (3, range(11, 17)),
]


def matricular_sofia(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    PerfilEstudiante = apps.get_model('plataforma', 'PerfilEstudiante')
    Materia = apps.get_model('plataforma', 'Materia')
    Periodo = apps.get_model('plataforma', 'Periodo')
    Matricula = apps.get_model('plataforma', 'Matricula')
    Planificacion = apps.get_model('plataforma', 'Planificacion')
    Parcial = apps.get_model('plataforma', 'Parcial')
    Unidad = apps.get_model('plataforma', 'Unidad')
    ActividadPlanificada = apps.get_model('plataforma', 'ActividadPlanificada')
    Tarea = apps.get_model('plataforma', 'Tarea')
    EntregaTarea = apps.get_model('plataforma', 'EntregaTarea')

    user = User.objects.filter(username='sofia.perez').first()
    if not user:
        return
    perfil = PerfilEstudiante.objects.filter(user=user).first()
    if not perfil:
        return

    periodo = Periodo.objects.filter(activo=True).order_by('-fecha_inicio').first()
    if not periodo:
        return

    ya_matriculada_ids = set(
        Matricula.objects.filter(estudiante=user, periodo=periodo).values_list('materia_id', flat=True)
    )
    materias = list(
        Materia.objects.filter(docente__isnull=False)
        .exclude(id__in=ya_matriculada_ids)
        .order_by('codigo')[:2]
    )
    if not materias:
        return

    for materia in materias:
        Matricula.objects.get_or_create(estudiante=user, materia=materia, periodo=periodo)

        planificacion = Planificacion.objects.filter(materia=materia, periodo=periodo).first()
        if not planificacion:
            planificacion = Planificacion.objects.create(
                materia=materia, periodo=periodo, docente=materia.docente,
            )
            for numero_parcial, semanas in _SEMANAS_POR_PARCIAL:
                parcial = Parcial.objects.create(
                    planificacion=planificacion, numero=numero_parcial, nombre=f'Parcial {numero_parcial}',
                )
                semanas = list(semanas)
                unidad = Unidad.objects.create(
                    parcial=parcial, numero=1, tema=f'Semanas {semanas[0]}-{semanas[-1]}',
                )
                ultima_semana = semanas[-1]
                for semana in semanas:
                    ActividadPlanificada.objects.create(
                        unidad=unidad, semana=semana, nombre=f'Semana {semana} - Actividad',
                        categoria='examen' if semana == ultima_semana else 'formativa',
                        fecha_entrega=periodo.fecha_inicio + timedelta(days=7 * semana),
                    )

        # Tareas reales sobre las primeras actividades, con fechas variadas
        # (la primera queda vencida a propósito para poblar "atrasada").
        actividades = list(
            ActividadPlanificada.objects.filter(
                unidad__parcial__planificacion=planificacion
            ).order_by('semana')[:3]
        )
        tareas_creadas = []
        for actividad in actividades:
            tarea, _ = Tarea.objects.get_or_create(
                materia=materia, actividad=actividad,
                defaults={
                    'titulo': actividad.nombre,
                    'descripcion': '',
                    'fecha_entrega': actividad.fecha_entrega,
                },
            )
            tareas_creadas.append(tarea)

        # La primera queda entregada; el resto, pendientes reales para
        # que "Próximas entregas" tenga datos con estados mixtos.
        if tareas_creadas:
            EntregaTarea.objects.get_or_create(
                tarea=tareas_creadas[0], estudiante=user,
                defaults={'estado': 'Entregado'},
            )


def revertir(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Matricula = apps.get_model('plataforma', 'Matricula')
    EntregaTarea = apps.get_model('plataforma', 'EntregaTarea')

    user = User.objects.filter(username='sofia.perez').first()
    if not user:
        return
    EntregaTarea.objects.filter(estudiante=user).delete()
    Matricula.objects.filter(estudiante=user).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0008_crear_usuario_docente'),
    ]

    operations = [
        migrations.RunPython(matricular_sofia, revertir),
    ]
