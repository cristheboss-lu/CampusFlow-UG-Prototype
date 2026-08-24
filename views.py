from django.shortcuts import render, redirect
from .models import Estudiante, Curso, Mensaje


def index(request):
    cursos = Curso.objects.all()
    return render(request, 'plataforma/index.html', {'cursos': cursos})


def aulas_virtuales(request):
    cursos = Curso.objects.all()
    return render(request, 'plataforma/aulas_virtuales.html', {'cursos': cursos})


def portal_estudiantil(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'plataforma/portal_estudiantil.html', {'estudiantes': estudiantes})


def biblioteca(request):
    return render(request, 'plataforma/biblioteca.html')


def admisiones(request):
    return render(request, 'plataforma/admisiones.html')


def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        Mensaje.objects.create(
            nombre=nombre,
            email=email,
            asunto=asunto,
            mensaje=mensaje
        )
        
        return redirect('contacto_exito')
    
    return render(request, 'plataforma/contacto.html')


def contacto_exito(request):
    return render(request, 'plataforma/contacto_exito.html')
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Usuario o clave incorrecta'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')

@login_required
def cursos_view(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos.html', {'cursos': cursos})