from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def index(request):
    """
    Página de inicio.
    Renderiza system/index.html que extiende de base.html.
    """
    return render(request, 'system/index.html')


def login_view(request):
    """
    Muestra y procesa el formulario de login.
    En POST, autentica y redirige a 'system:home' si tiene éxito,
    o vuelve a mostrar el formulario con mensaje de error.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('system:home')
        else:
            # Falló autenticación
            return render(request, 'system/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
    # GET: renderizar formulario
    return render(request, 'system/login.html')

def quienes_somos(request):
    return render(request, 'system/quienes_somos.html')

def servicios(request):
    return render(request, 'system/servicios.html')

def contactanos(request):
    return render(request, 'system/contactanos.html')

def cursos(request):
    return render(request, 'system/cursos.html')

def certificados(request):
    """
    Página simple para ingresar el código de certificado
    (aún sin lógica de búsqueda).
    """
    return render(request, 'system/certificados.html')

