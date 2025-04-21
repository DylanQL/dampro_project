from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from functools import wraps
from .models import *


def index(request):
    """
    Página de inicio.
    Renderiza system/index.html que extiende de base.html.
    """
    return render(request, 'system/index.html')

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

# Decorador para comprobar sesión
def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('system:login')
        return view_func(request, *args, **kwargs)
    return wrapped_view

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = UserAccount.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect('system:home_logged')
        except UserAccount.DoesNotExist:
            return render(request, 'system/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
    return render(request, 'system/login.html')

@login_required
def home_logged(request):
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    return render(request, 'system/home_logged.html', {'user': user})

def logout_view(request):
    request.session.flush()  # elimina toda la sesión
    return redirect('system:login')


@login_required
def gestion_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'system/gestion_usuarios.html', {
        'usuarios': usuarios
    })

@login_required
def add_usuario(request):
    if request.method == 'POST':
        # Leer datos del formulario
        first = request.POST.get('first_name', '').strip()
        middle = request.POST.get('middle_name', '').strip() or None
        last = request.POST.get('last_name', '').strip()
        second_last = request.POST.get('second_last_name', '').strip() or None
        utype = request.POST.get('user_type', '').strip()

        # Crear y guardar
        Usuario.objects.create(
            first_name=first,
            middle_name=middle,
            last_name=last,
            second_last_name=second_last,
            user_type=utype
        )
        return redirect('system:gestion_usuarios')

    return render(request, 'system/usuario_form.html', {
        'action': 'add',
        'usuario': None
    })

@login_required
def edit_usuario(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    if request.method == 'POST':
        usuario.first_name       = request.POST.get('first_name', usuario.first_name).strip()
        usuario.middle_name      = request.POST.get('middle_name', usuario.middle_name).strip() or None
        usuario.last_name        = request.POST.get('last_name', usuario.last_name).strip()
        usuario.second_last_name = request.POST.get('second_last_name', usuario.second_last_name).strip() or None
        usuario.user_type        = request.POST.get('user_type', usuario.user_type).strip()
        usuario.save()
        return redirect('system:gestion_usuarios')

    return render(request, 'system/usuario_form.html', {
        'action': 'edit',
        'usuario': usuario
    })


@login_required
def gestion_cursos(request):
    cursos = Course.objects.all()
    return render(request, 'system/gestion_cursos.html', {
        'cursos': cursos
    })

@login_required
def add_curso(request):
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        hours = request.POST.get('course_hours', '0').strip()
        Course.objects.create(
            name=name,
            course_hours=int(hours)
        )
        return redirect('system:gestion_cursos')
    return render(request, 'system/curso_form.html', {
        'action': 'add',
        'curso': None
    })

@login_required
def edit_curso(request, pk):
    curso = Course.objects.get(pk=pk)
    if request.method == 'POST':
        curso.name = request.POST.get('name', curso.name).strip()
        curso.course_hours = int(request.POST.get('course_hours', curso.course_hours))
        curso.save()
        return redirect('system:gestion_cursos')
    return render(request, 'system/curso_form.html', {
        'action': 'edit',
        'curso': curso
    })