from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from openpyxl import load_workbook
from .models import (
    Curso, Estudiante, Mensaje, PerfilEstudiante, Carrera
)

def index(request):
    """Página principal"""
    return render(request, 'plataforma/index.html')

def aulas_virtuales(request):
    """Aulas virtuales"""
    cursos = Curso.objects.all()
    return render(request, 'plataforma/aulas_virtuales.html', {'cursos': cursos})

def portal_estudiantil(request):
    """Portal estudiantil"""
    return render(request, 'plataforma/portal_estudiantil.html')

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
        
        # Guardar en BD
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

@login_required
def importar_estudiantes(request):
    """Importar estudiantes desde Excel"""
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']
        
        try:
            # Cargar el archivo Excel
            wb = load_workbook(archivo)
            ws = wb.active
            
            contador_creados = 0
            contador_errores = 0
            errores = []
            
            # Iterar desde la fila 2 (la 1 es encabezado)
            for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    # Extraer datos: nombre, apellido, email, cedula, numero_matricula, carrera_id
                    nombre = fila[0]
                    apellido = fila[1]
                    email = fila[2]
                    cedula = fila[3]
                    numero_matricula = fila[4]
                    carrera_id = fila[5]
                    
                    # Validar que no estén vacíos
                    if not all([nombre, apellido, email, cedula, numero_matricula]):
                        errores.append(f"Fila {fila_num}: Faltan datos obligatorios")
                        contador_errores += 1
                        continue
                    
                    # Crear usuario
                    username = str(email).split('@')[0]
                    if User.objects.filter(username=username).exists():
                        errores.append(f"Fila {fila_num}: El usuario {username} ya existe")
                        contador_errores += 1
                        continue
                    
                    # Verificar que la carrera existe
                    try:
                        carrera = Carrera.objects.get(id=int(carrera_id))
                    except Carrera.DoesNotExist:
                        errores.append(f"Fila {fila_num}: La carrera con ID {carrera_id} no existe")
                        contador_errores += 1
                        continue
                    
                    # Crear el usuario
                    usuario = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=nombre,
                        last_name=apellido,
                        password='Temporal123!'
                    )
                    
                    # Crear perfil de estudiante
                    PerfilEstudiante.objects.create(
                        user=usuario,
                        carrera=carrera,
                        cedula=str(cedula),
                        numero_matricula=str(numero_matricula)
                    )
                    
                    contador_creados += 1
                    
                except Exception as e:
                    errores.append(f"Fila {fila_num}: {str(e)}")
                    contador_errores += 1
            
            # Mostrar mensajes
            if contador_creados > 0:
                messages.success(request, f"✅ {contador_creados} estudiantes importados correctamente")
            
            if errores:
                for error in errores[:10]:  # Mostrar máximo 10 errores
                    messages.warning(request, error)
            
            if contador_errores > 10:
                messages.info(request, f"... y {contador_errores - 10} errores más")
            
            return redirect('importar_estudiantes')
        
        except Exception as e:
            messages.error(request, f"❌ Error al importar: {str(e)}")
    
    carreras = Carrera.objects.all()
    return render(request, 'plataforma/importar_estudiantes.html', {'carreras': carreras})
