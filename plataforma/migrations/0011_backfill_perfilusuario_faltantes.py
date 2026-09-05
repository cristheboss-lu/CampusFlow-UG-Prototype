from django.db import migrations


def backfill_perfilusuario(apps, schema_editor):
    """
    Crea el PerfilUsuario que le falta a cualquier PerfilEstudiante/PerfilDocente
    que no lo tenga. Detectado en producción: 33 de 33 estudiantes existentes no
    tenían PerfilUsuario (datos previos al código actual, que sí lo crea siempre
    en sus tres caminos de alta). Idempotente: en una segunda corrida no encuentra
    a nadie pendiente.
    """
    PerfilUsuario = apps.get_model('plataforma', 'PerfilUsuario')
    PerfilEstudiante = apps.get_model('plataforma', 'PerfilEstudiante')
    PerfilDocente = apps.get_model('plataforma', 'PerfilDocente')

    user_ids_con_perfil = set(PerfilUsuario.objects.values_list('user_id', flat=True))

    estudiantes_sin_perfil = PerfilEstudiante.objects.exclude(user_id__in=user_ids_con_perfil)
    PerfilUsuario.objects.bulk_create([
        PerfilUsuario(user_id=pe.user_id, rol='estudiante')
        for pe in estudiantes_sin_perfil
    ])

    docentes_sin_perfil = PerfilDocente.objects.exclude(user_id__in=user_ids_con_perfil)
    PerfilUsuario.objects.bulk_create([
        PerfilUsuario(user_id=pd.user_id, rol='docente')
        for pd in docentes_sin_perfil
    ])


def revertir(apps, schema_editor):
    """
    No hay una forma segura de distinguir, después del hecho, cuáles
    PerfilUsuario fueron creados por este backfill de cuáles ya existían
    antes — revertir a ciegas por (user_id, rol) arriesgaría borrar filas
    legítimas. Se deja como no-op intencional.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0010_certificado_estado_alter_certificado_fecha_emision_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_perfilusuario, revertir),
    ]
