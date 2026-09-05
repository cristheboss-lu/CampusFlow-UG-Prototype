from django.db import migrations
from django.contrib.auth.hashers import make_password


def crear_docente(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    PerfilUsuario = apps.get_model('plataforma', 'PerfilUsuario')
    PerfilDocente = apps.get_model('plataforma', 'PerfilDocente')
    Materia = apps.get_model('plataforma', 'Materia')
    Carrera = apps.get_model('plataforma', 'Carrera')

    if User.objects.filter(username='docente').exists():
        return

    # Preferir una materia sin docente asignado, para no quitarle su materia
    # a un docente real ya existente.
    materia_libre = Materia.objects.filter(docente__isnull=True).first()
    materia_con_docente = None if materia_libre else Materia.objects.first()
    carrera = (materia_libre or materia_con_docente).carrera if (materia_libre or materia_con_docente) else None

    if not carrera:
        carrera, _ = Carrera.objects.get_or_create(
            codigo='PRUEBA', defaults={'nombre': 'Carrera de Prueba'}
        )

    user = User.objects.create(
        username='docente',
        email='docente@tuinstitucion.edu',
        first_name='Docente',
        last_name='De Prueba',
        password=make_password('docente123'),
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )

    PerfilUsuario.objects.create(
        user=user,
        rol='docente',
    )

    perfil_docente = PerfilDocente.objects.create(
        user=user,
        carrera=carrera,
        cedula='0000000001',
        titulo_academico='Docente de prueba',
    )

    if materia_libre:
        materia_libre.docente = perfil_docente
        materia_libre.save(update_fields=['docente'])
    else:
        # Todas las materias existentes ya tienen docente: crear una dedicada
        # en vez de quitarle la suya a un docente real.
        Materia.objects.create(
            nombre='Materia de Prueba',
            codigo='PRUEBA-101',
            carrera=carrera,
            docente=perfil_docente,
        )


def revertir(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='docente').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0007_tarea_actividad'),
    ]

    operations = [
        migrations.RunPython(crear_docente, revertir),
    ]
