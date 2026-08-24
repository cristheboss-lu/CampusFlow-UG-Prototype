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