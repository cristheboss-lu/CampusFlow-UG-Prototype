from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    return render(request, 'plataforma/index.html')

def aulas_virtuales(request):
    return render(request, 'plataforma/aulas_virtuales.html')

def portal_estudiantil(request):
    return render(request, 'plataforma/portal_estudiantil.html')

def biblioteca(request):
    return render(request, 'plataforma/biblioteca.html')

def admisiones(request):
    return render(request, 'plataforma/admisiones.html')

def contacto(request):
    return render(request, 'plataforma/contacto.html')

def contacto_exito(request):
    return render(request, 'plataforma/contacto_exito.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('cursos')
        else:
            messages.error(request, 'Usuario o contraseña incorrecta')
    return render(request, 'plataforma/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='/login/')
def cursos_view(request):
    return render(request, 'plataforma/cursos.html')
