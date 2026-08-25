from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# --- Páginas públicas ---
def index(request):
    return render(request, 'plataforma/index.html')

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

# --- Login centrado para Aula Virtual ---
def login_view(request):
    # Si ya está logueado, no mostrar login, ir directo a aulas
    if request.user.is_authenticated:
        return redirect('aulas_virtuales')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirige a donde quería ir o a aulas-virtuales
            next_url = request.GET.get('next') or 'aulas_virtuales'
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrecta')
    
    return render(request, 'plataforma/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

# --- Área protegida ---
@login_required(login_url='/login/')
def aulas_virtuales(request):
    # Aquí va tu lógica real de cursos del usuario
    # Por ahora vacío para que no de error, luego pones tu query
    cursos = [] 
    return render(request, 'plataforma/aulas_virtuales.html', {'cursos': cursos})

@login_required(login_url='/login/')
def cursos_view(request):
    return render(request, 'plataforma/cursos.html')
