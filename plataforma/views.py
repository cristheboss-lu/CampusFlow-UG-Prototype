from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from openpyxl import load_workbook
from .models import (
    Materia, Mensaje, PerfilEstudiante, Carrera, Matricula, Tarea, EntregaTarea
)

def index(request):
    """Página principal"""
    return render(request, 'plataforma/index.html')

def aulas_virtuales(request):
    """Aulas virtuales - redirige a login o al dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard_estudiante')
    return redirect('login')

def portal_estudiantil(request):
    """Portal estudiantil - lista de estudiantes con su carrera"""
    estudiantes = PerfilEstudiante.objects.select_related('user', 'carrera').filter(activo=True)
    return render(request, 'plataforma/portal_estudiante.html', {'estudiantes': estudiantes})

def biblioteca(request):
    """Biblioteca digital"""
    return render(request, 'plataforma/biblioteca.html')

def admisiones(request):
    """Admisiones"""
    return render(request, 'plataforma/admisiones.html')

def contacto(request):
    """Formulario de contacto"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje_texto = request.POST.get('mensaje')

        Mensaje.objects.create(
            nombre=nombre,
            email=email,
            asunto=asunto,
            mensaje=mensaje_texto
        )

        return redirect('contacto_exito')

    return render(request, 'plataforma/contacto.html')

def contacto_exito(request):
    """Página de éxito del contacto"""
    return render(request, 'plataforma/contacto_exito.html')


# ===== AUTENTICACIÓN DE ESTUDIANTES =====

def login_estudiante(request):
    """Login para estudiantes"""
    if request.user.is_authenticated:
        return redirect('dashboard_estudiante')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard_estudiante')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')

    return render(request, 'plataforma/login.html')

def logout_estudiante(request):
    """Cerrar sesión"""
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def dashboard_estudiante(request):
    """Panel del estudiante: sus materias matriculadas y tareas pendientes"""
    matriculas = Matricula.objects.filter(estudiante=request.user).select_related('materia', 'periodo')

    materias_ids = matriculas.values_list('materia_id', flat=True)
    tareas = Tarea.objects.filter(materia_id__in=materias_ids).select_related('materia').order_by('fecha_entrega')

    entregas_usuario = EntregaTarea.objects.filter(estudiante=request.user)
    entregas_dict = {e.tarea_id: e for e in entregas_usuario}

    tareas_con_estado = []
    for tarea in tareas:
        entrega = entregas_dict.get(tarea.id)
        tareas_con_estado.append({
            'tarea': tarea,
            'entrega': entrega,
            'estado': entrega.estado if entrega else 'Pendiente',
        })

    return render(request, 'plataforma/panel_estudiante.html', {
        'matriculas': matriculas,
        'tareas_con_estado': tareas_con_estado,
    })


# ===== IMPORTAR DATOS DESDE EXCEL (multi-entidad) =====

def _importar_estudiantes_desde_excel(ws):
    """Procesa un Excel de estudiantes. Columnas: Nombre, Apellido, Email, Cédula, Nº Matrícula, Carrera ID"""
    password_hash = make_password('Temporal123!')
    carreras_dict = {c.id: c for c in Carrera.objects.all()}
    usernames_existentes = set(User.objects.values_list('username', flat=True))

    usuarios_a_crear = []
    filas_validas = []
    errores = []
    usernames_en_lote = set()

    for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            nombre, apellido, email, cedula, numero_matricula, carrera_id = fila[0:6]

            if not all([nombre, apellido, email, cedula, numero_matricula]):
                errores.append(f"Fila {fila_num}: Faltan datos obligatorios")
                continue

            username = str(email).split('@')[0]

            if username in usernames_existentes or username in usernames_en_lote:
                errores.append(f"Fila {fila_num}: El usuario {username} ya existe")
                continue

            carrera = carreras_dict.get(int(carrera_id))
            if not carrera:
                errores.append(f"Fila {fila_num}: La carrera con ID {carrera_id} no existe")
                continue

            usernames_en_lote.add(username)

            usuarios_a_crear.append(User(
                username=username, email=email,
                first_name=nombre, last_name=apellido,
                password=password_hash
            ))
            filas_validas.append((username, cedula, numero_matricula, carrera))

        except Exception as e:
            errores.append(f"Fila {fila_num}: {str(e)}")

    User.objects.bulk_create(usuarios_a_crear)

    usuarios_creados = {
        u.username: u for u in User.objects.filter(username__in=[f[0] for f in filas_validas])
    }

    perfiles_a_crear = []
    for username, cedula, numero_matricula, carrera in filas_validas:
        usuario_obj = usuarios_creados.get(username)
        if usuario_obj:
            perfiles_a_crear.append(PerfilEstudiante(
                user=usuario_obj, carrera=carrera,
                cedula=str(cedula), numero_matricula=str(numero_matricula)
            ))

    PerfilEstudiante.objects.bulk_create(perfiles_a_crear)
    return len(perfiles_a_crear), errores


def _importar_carreras_desde_excel(ws):
    """Procesa un Excel de carreras. Columnas: Nombre, Código, Descripción, Créditos totales"""
    codigos_existentes = set(Carrera.objects.values_list('codigo', flat=True))
    carreras_a_crear = []
    errores = []
    codigos_en_lote = set()

    for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            nombre, codigo = fila[0], fila[1]
            descripcion = fila[2] if len(fila) > 2 and fila[2] else ''
            creditos_totales = fila[3] if len(fila) > 3 and fila[3] else 120

            if not all([nombre, codigo]):
                errores.append(f"Fila {fila_num}: Faltan datos obligatorios")
                continue

            if codigo in codigos_existentes or codigo in codigos_en_lote:
                errores.append(f"Fila {fila_num}: El código de carrera {codigo} ya existe")
                continue

            codigos_en_lote.add(codigo)
            carreras_a_crear.append(Carrera(
                nombre=nombre, codigo=codigo,
                descripcion=descripcion, creditos_totales=int(creditos_totales)
            ))

        except Exception as e:
            errores.append(f"Fila {fila_num}: {str(e)}")

    Carrera.objects.bulk_create(carreras_a_crear)
    return len(carreras_a_crear), errores


def _importar_materias_desde_excel(ws):
    """Procesa un Excel de materias. Columnas: Nombre, Código, Carrera ID, Créditos, Profesor"""
    carreras_dict = {c.id: c for c in Carrera.objects.all()}
    codigos_existentes = set(Materia.objects.values_list('codigo', flat=True))
    materias_a_crear = []
    errores = []
    codigos_en_lote = set()

    for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            nombre, codigo, carrera_id = fila[0], fila[1], fila[2]
            creditos = fila[3] if len(fila) > 3 and fila[3] else 4
            profesor = fila[4] if len(fila) > 4 and fila[4] else ''

            if not all([nombre, codigo, carrera_id]):
                errores.append(f"Fila {fila_num}: Faltan datos obligatorios")
                continue

            if codigo in codigos_existentes or codigo in codigos_en_lote:
                errores.append(f"Fila {fila_num}: El código de materia {codigo} ya existe")
                continue

            carrera = carreras_dict.get(int(carrera_id))
            if not carrera:
                errores.append(f"Fila {fila_num}: La carrera con ID {carrera_id} no existe")
                continue

            codigos_en_lote.add(codigo)
            materias_a_crear.append(Materia(
                nombre=nombre, codigo=codigo, carrera=carrera,
                creditos=int(creditos), profesor=profesor
            ))

        except Exception as e:
            errores.append(f"Fila {fila_num}: {str(e)}")

    Materia.objects.bulk_create(materias_a_crear)
    return len(materias_a_crear), errores


@staff_member_required
def importar_estudiantes(request):
    """Importación masiva de datos (Estudiantes, Carreras o Materias) desde Excel"""
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']
        tipo = request.POST.get('tipo_importacion', 'estudiantes')

        try:
            wb = load_workbook(archivo)
            ws = wb.active

            if tipo == 'estudiantes':
                contador, errores = _importar_estudiantes_desde_excel(ws)
                etiqueta = 'estudiantes'
            elif tipo == 'carreras':
                contador, errores = _importar_carreras_desde_excel(ws)
                etiqueta = 'carreras'
            elif tipo == 'materias':
                contador, errores = _importar_materias_desde_excel(ws)
                etiqueta = 'materias'
            elif tipo == 'docentes':
                # Aún no existe un modelo de Docente/PerfilDocente en el sistema.
                messages.error(request, "❌ La importación de docentes todavía no está disponible: falta crear el modelo correspondiente.")
                return redirect('importar_estudiantes')
            else:
                messages.error(request, "❌ Tipo de importación no reconocido")
                return redirect('importar_estudiantes')

            if contador > 0:
                messages.success(request, f"✅ {contador} {etiqueta} importados correctamente")

            if errores:
                for error in errores[:10]:
                    messages.warning(request, error)
                if len(errores) > 10:
                    messages.info(request, f"... y {len(errores) - 10} errores más")

            return redirect('importar_estudiantes')

        except Exception as e:
            messages.error(request, f"❌ Error al importar: {str(e)}")

    carreras = Carrera.objects.all()
    return render(request, 'plataforma/importar_estudiantes.html', {'carreras': carreras})
