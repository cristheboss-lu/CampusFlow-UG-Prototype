from django.db import migrations
from django.contrib.auth.hashers import make_password

def crear_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    PerfilUsuario = apps.get_model('plataforma', 'PerfilUsuario')

    if User.objects.filter(username='secretaria').exists():
        return

    user = User.objects.create(
        username='secretaria',
        email='secretaria@tuinstitucion.edu',
        first_name='Secretaria',
        last_name='General',
        password=make_password('secretaria123'),
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )

    PerfilUsuario.objects.create(
        user=user,
        cedula='0000000000',
        rol='admin',
    )

def revertir(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='secretaria').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0002_bibliotecadigital_calificacion_carrera_certificado_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_admin, revertir),
    ]
