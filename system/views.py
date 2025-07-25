from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.urls import reverse
from functools import wraps
from .models import *
from django.db import models
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.conf import settings
import os
import qrcode
from io import BytesIO
import base64
import string
import random
import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
import json


def get_mes_completo_espanol(numero_mes):
    """
    Convierte un número de mes en el nombre completo en español.
    """
    meses_espanol = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre'
    }
    return meses_espanol.get(numero_mes, '')


def generate_unique_cert_code(length=10):
    """
    Genera un código de certificado aleatorio único.
    
    Args:
        length: La longitud del código a generar (sin incluir el prefijo)
    
    Returns:
        Un código de certificado que no existe en la base de datos
    """
    # Caracteres para generar el código (letras mayúsculas y números)
    characters = string.ascii_uppercase + string.digits
    
    while True:
        # Prefijo para identificar que es un certificado
        prefix = "CERT-"
        
        # Generar código aleatorio
        random_part = ''.join(random.choice(characters) for _ in range(length))
        
        # Combinar prefijo con parte aleatoria
        cert_code = f"{prefix}{random_part}"
        
        # Verificar si ya existe en la base de datos
        if not Certificate.objects.filter(cert_code=cert_code).exists():
            return cert_code


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

def programas(request):
    return render(request, 'system/programas.html')

def certificados(request):
    """
    Página para verificar certificados mediante su código.
    Si se proporciona un código, redirecciona a la vista de detalle del certificado.
    """
    if 'cert_code' in request.GET:
        cert_code = request.GET.get('cert_code').strip()
        return redirect('system:certificado_detail', cert_code=cert_code)
    
    return render(request, 'system/certificados.html')

def certificado_detail(request, cert_code):
    """
    Página que muestra el detalle de un certificado específico.
    """
    certificado = None
    error = None
    mes_espanol = None
    
    try:
        certificado = Certificate.objects.select_related('usuario', 'program', 'empresa').get(cert_code=cert_code)
        # Obtener el mes en español completo
        if certificado:
            mes_numero = certificado.creation_date.month
            mes_espanol = get_mes_completo_espanol(mes_numero)
    except Certificate.DoesNotExist:
        error = f"No se encontró ningún certificado con el código: {cert_code}"
    
    return render(request, 'system/certificado_detail.html', {
        'certificado': certificado,
        'error': error,
        'mes_espanol': mes_espanol
    })

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
    
    # Count the records for dashboard display
    usuarios_count = Usuario.objects.filter(user_type="Empleado").count()
    empresas_count = Empresa.objects.count()
    programas_count = TrainingProgram.objects.count()
    certificados_count = Certificate.objects.count()
    
    return render(request, 'system/home_logged.html', {
        'user': user,
        'usuarios_count': usuarios_count,
        'empresas_count': empresas_count,
        'programas_count': programas_count,
        'certificados_count': certificados_count
    })

def logout_view(request):
    request.session.flush()  # elimina toda la sesión
    return redirect('system:login')


@login_required
def gestion_usuarios(request):
    from django.core.paginator import Paginator
    
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    # Obtener todas las empresas para el filtro
    empresas = Empresa.objects.all()
    
    # Filtrar usuarios por empresa si se proporciona un ID de empresa
    empresa_id = request.GET.get('empresa_id')
    
    if empresa_id and empresa_id.isdigit() and int(empresa_id) > 0:
        # Filtrar por empresa específica y solo usuarios tipo Empleado
        usuarios_list = Usuario.objects.filter(empresa_id=int(empresa_id), user_type="Empleado")
        empresa_seleccionada = int(empresa_id)
    elif empresa_id == 'sin_empresa':
        # Filtrar usuarios sin empresa asignada y solo usuarios tipo Empleado
        usuarios_list = Usuario.objects.filter(empresa__isnull=True, user_type="Empleado")
        empresa_seleccionada = 'sin_empresa'
    else:
        # Mostrar todos los usuarios tipo Empleado si no hay filtro o si es "todos"
        usuarios_list = Usuario.objects.filter(user_type="Empleado")
        empresa_seleccionada = 'todos'
    
    # Aplicar paginación
    paginator = Paginator(usuarios_list, 10)  # 10 usuarios por página
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)
    
    return render(request, 'system/gestion_usuarios.html', {
        'user': user,
        'usuarios': usuarios,
        'empresas': empresas,
        'empresa_seleccionada': empresa_seleccionada
    })

@login_required
def add_usuario(request):
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    if request.method == 'POST':
        # Leer datos del formulario
        first = request.POST.get('first_name', '').strip()
        last = request.POST.get('last_name', '').strip()
        second_last = request.POST.get('second_last_name', '').strip() or None
        numero_documento = request.POST.get('numero_documento', '').strip() or None
        tipo_documento = request.POST.get('tipo_documento', 'DNI').strip()
        utype = "Empleado"
        empresa_id = request.POST.get('empresa_id', '')

        # Validar que el número de documento no esté vacío
        if not numero_documento:
            empresas = Empresa.objects.all()
            return render(request, 'system/usuario_form.html', {
                'user': user,
                'action': 'add',
                'usuario': None,
                'empresas': empresas,
                'error_message': 'El número de documento es obligatorio.'
            })
        # Comprobar si el número de documento ya existe
        if Usuario.objects.filter(numero_documento=numero_documento).exists():
            empresas = Empresa.objects.all()
            return render(request, 'system/usuario_form.html', {
                'user': user,
                'action': 'add',
                'usuario': None,
                'empresas': empresas,
                'error_message': 'El número de documento ingresado ya se encuentra registrado.'
            })
        
        # Obtener la empresa si se proporcionó un ID
        empresa = None
        if empresa_id:
            try:
                empresa = Empresa.objects.get(pk=int(empresa_id))
            except (Empresa.DoesNotExist, ValueError):
                pass

        # Crear y guardar
        Usuario.objects.create(
            first_name=first,
            last_name=last,
            second_last_name=second_last,
            numero_documento=numero_documento,
            tipo_documento=tipo_documento,
            user_type=utype,
            empresa=empresa
        )
        return redirect('system:gestion_usuarios')
    
    empresas = Empresa.objects.all()
    return render(request, 'system/usuario_form.html', {
        'user': user,
        'action': 'add',
        'usuario': None,
        'empresas': empresas
    })

@login_required
def edit_usuario(request, pk):
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    usuario = Usuario.objects.get(pk=pk)
    if request.method == 'POST':
        usuario.first_name       = request.POST.get('first_name', usuario.first_name).strip()
        usuario.last_name        = request.POST.get('last_name', usuario.last_name).strip()
        usuario.second_last_name = request.POST.get('second_last_name', usuario.second_last_name).strip() or None
        numero_documento         = request.POST.get('numero_documento', usuario.numero_documento).strip() or None
        usuario.tipo_documento   = request.POST.get('tipo_documento', usuario.tipo_documento).strip() or 'DNI'
        usuario.user_type        = request.POST.get('user_type', usuario.user_type).strip()
        
        # Validar que el número de documento no esté vacío
        if not numero_documento:
            empresas = Empresa.objects.all()
            return render(request, 'system/usuario_form.html', {
                'user': user,
                'action': 'edit',
                'usuario': usuario,
                'empresas': empresas,
                'error_message': 'El número de documento es obligatorio.'
            })
        usuario.numero_documento = numero_documento
        
        # Actualizar la relación con la empresa
        empresa_id = request.POST.get('empresa_id', '')
        if empresa_id:
            try:
                usuario.empresa = Empresa.objects.get(pk=int(empresa_id))
            except (Empresa.DoesNotExist, ValueError):
                usuario.empresa = None
        else:
            usuario.empresa = None
            
        usuario.save()
        return redirect('system:gestion_usuarios')

    empresas = Empresa.objects.all()
    return render(request, 'system/usuario_form.html', {
        'user': user,
        'action': 'edit',
        'usuario': usuario,
        'empresas': empresas
    })


@login_required
def gestion_programas(request):
    from django.core.paginator import Paginator
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    tipo = request.GET.get('tipo', '').strip()
    programas_list = TrainingProgram.objects.all()
    if tipo:
        programas_list = programas_list.filter(program_type__iexact=tipo)
    paginator = Paginator(programas_list, 10)
    page_number = request.GET.get('page')
    programas = paginator.get_page(page_number)
    return render(request, 'system/gestion_programas.html', {
        'user': user,
        'programas': programas,
        'tipo_filtro': tipo
    })

@login_required
def add_programa(request):
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        hours = request.POST.get('hours', '0').strip()
        program_type = request.POST.get('program_type', '').strip()
        TrainingProgram.objects.create(
            name=name,
            hours=int(hours),
            program_type=program_type
        )
        return redirect('system:gestion_programas')
    return render(request, 'system/programa_form.html', {
        'user': user,
        'action': 'add',
        'programa': None
    })

@login_required
def edit_programa(request, pk):
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    programa = TrainingProgram.objects.get(pk=pk)
    if request.method == 'POST':
        programa.name = request.POST.get('name', programa.name).strip()
        programa.hours = int(request.POST.get('hours', programa.hours))
        programa.program_type = request.POST.get('program_type', programa.program_type).strip()
        programa.save()
        return redirect('system:gestion_programas')
    return render(request, 'system/programa_form.html', {
        'user': user,
        'action': 'edit',
        'programa': programa
    })


@login_required
def gestion_certificados(request):
    from django.core.paginator import Paginator
    
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    certificados_list = Certificate.objects.select_related('usuario', 'program', 'empresa').all().order_by('-creation_date')
    paginator = Paginator(certificados_list, 10)  # 10 certificados por página
    
    page_number = request.GET.get('page')
    certificados = paginator.get_page(page_number)
    
    return render(request, 'system/gestion_certificados.html', {
        'user': user,
        'certificados': certificados
    })

@login_required
def add_certificado(request):
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        program_id  = request.POST.get('program_id')  # Cambiado de course_id a program_id para coincidir con el formulario
        horas      = request.POST.get('chronological_hours', '0').strip() or '0'
        creation_date = request.POST.get('creation_date')

        # Validaciones de seguridad
        if not usuario_id or not program_id:
            usuarios = Usuario.objects.all()
            programas = TrainingProgram.objects.all()
            empresas = Empresa.objects.all()
            
            from django.utils import timezone
            from zoneinfo import ZoneInfo
            lima_tz = ZoneInfo('America/Lima')
            fecha_actual_peru = timezone.now().astimezone(lima_tz)
            
            return render(request, 'system/certificado_form.html', {
                'user': user,
                'action': 'add',
                'certificado': None,
                'usuarios': usuarios,
                'programas': programas,
                'empresas': empresas,
                'fecha_actual': fecha_actual_peru,
                'error_message': 'Debe seleccionar un cliente y un programa válidos.'
            })

        try:
            usuario = get_object_or_404(Usuario, pk=int(usuario_id), user_type="Empleado")
            program = get_object_or_404(TrainingProgram, pk=int(program_id))
        except (ValueError, Usuario.DoesNotExist, TrainingProgram.DoesNotExist):
            usuarios = Usuario.objects.all()
            programas = TrainingProgram.objects.all()
            empresas = Empresa.objects.all()
            
            from django.utils import timezone
            from zoneinfo import ZoneInfo
            lima_tz = ZoneInfo('America/Lima')
            fecha_actual_peru = timezone.now().astimezone(lima_tz)
            
            return render(request, 'system/certificado_form.html', {
                'user': user,
                'action': 'add',
                'certificado': None,
                'usuarios': usuarios,
                'programas': programas,
                'empresas': empresas,
                'fecha_actual': fecha_actual_peru,
                'error_message': 'El cliente o programa seleccionado no es válido.'
            })

        # Generar un código aleatorio único para el certificado
        cert_code = generate_unique_cert_code()
        
        # Obtener automáticamente la empresa del usuario
        empresa = usuario.empresa
        
        # Obtener la modalidad seleccionada
        modality = request.POST.get('modality')
        
        # Crear el certificado
        certificado = Certificate(
            usuario=usuario,
            program=program,
            empresa=empresa,
            chronological_hours=int(horas),
            cert_code=cert_code,
            modality=modality
        )
        
        # Establecer la fecha si se proporcionó una personalizada
        if creation_date:
            from datetime import datetime
            from django.utils import timezone
            from zoneinfo import ZoneInfo
            try:
                # Parsear la fecha como naive datetime
                naive_date = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M')
                # Convertir a timezone-aware con zona horaria de Perú
                lima_tz = ZoneInfo('America/Lima')
                certificado.creation_date = naive_date.replace(tzinfo=lima_tz)
            except ValueError:
                # Si hay un problema con el formato, usar la fecha actual (valor por defecto)
                pass
        
        certificado.save()
        return redirect('system:gestion_certificados')

    usuarios = Usuario.objects.all()
    programas = TrainingProgram.objects.all()
    empresas = Empresa.objects.all()
    
    # Obtener la fecha y hora actual en zona horaria de Perú
    from django.utils import timezone
    from zoneinfo import ZoneInfo
    
    # Crear datetime actual en zona horaria de Perú
    lima_tz = ZoneInfo('America/Lima')
    fecha_actual_peru = timezone.now().astimezone(lima_tz)
    
    return render(request, 'system/certificado_form.html', {
        'user': user,
        'action': 'add',
        'certificado': None,
        'usuarios': usuarios,
        'programas': programas,
        'empresas': empresas,
        'fecha_actual': fecha_actual_peru,
    })

@login_required
def edit_certificado(request, pk):
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    certificado = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        program_id = request.POST.get('program_id')  # Cambiado de course_id a program_id para coincidir con el formulario
        empresa_id = request.POST.get('empresa_id')
        horas      = request.POST.get('chronological_hours', certificado.chronological_hours)
        creation_date = request.POST.get('creation_date')

        # Validaciones de seguridad
        if not usuario_id or not program_id:
            usuarios = Usuario.objects.all()
            programas = TrainingProgram.objects.all()
            empresas = Empresa.objects.all()
            return render(request, 'system/certificado_form.html', {
                'user': user,
                'action': 'edit',
                'certificado': certificado,
                'usuarios': usuarios,
                'programas': programas,
                'empresas': empresas,
                'error_message': 'Debe seleccionar un cliente y un programa válidos.'
            })

        try:
            usuario = get_object_or_404(Usuario, pk=int(usuario_id), user_type="Empleado")
            certificado.usuario = usuario
            certificado.program = get_object_or_404(TrainingProgram, pk=int(program_id))
        except (ValueError, Usuario.DoesNotExist, TrainingProgram.DoesNotExist):
            usuarios = Usuario.objects.all()
            programas = TrainingProgram.objects.all()
            empresas = Empresa.objects.all()
            return render(request, 'system/certificado_form.html', {
                'user': user,
                'action': 'edit',
                'certificado': certificado,
                'usuarios': usuarios,
                'programas': programas,
                'empresas': empresas,
                'error_message': 'El cliente o programa seleccionado no es válido.'
            })
        
        # Permitir la selección manual de la empresa
        if empresa_id:
            try:
                certificado.empresa = get_object_or_404(Empresa, pk=int(empresa_id))
            except (ValueError, Empresa.DoesNotExist):
                certificado.empresa = None
        else:
            certificado.empresa = None
        
        certificado.chronological_hours = int(horas)
        
        # Actualizar la modalidad
        modality = request.POST.get('modality')
        certificado.modality = modality
        
        # Actualizar la fecha si se proporcionó una nueva
        if creation_date:
            from datetime import datetime
            from django.utils import timezone
            from zoneinfo import ZoneInfo
            # Convertir la cadena de fecha-hora en un objeto datetime
            # El formato debe ser compatible con el formato datetime-local de HTML5
            try:
                # Parsear la fecha como naive datetime
                naive_date = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M')
                # Convertir a timezone-aware con zona horaria de Perú
                lima_tz = ZoneInfo('America/Lima')
                certificado.creation_date = naive_date.replace(tzinfo=lima_tz)
            except ValueError:
                # Si hay un problema con el formato, mantenemos la fecha actual
                pass
                
        certificado.save()
        return redirect('system:gestion_certificados')

    usuarios = Usuario.objects.all()
    programas = TrainingProgram.objects.all()
    empresas = Empresa.objects.all()
    return render(request, 'system/certificado_form.html', {
        'user': user,
        'action': 'edit',
        'certificado': certificado,
        'usuarios': usuarios,
        'programas': programas,
        'empresas': empresas,
    })

@login_required
def certificado_pdf(request, cert_code):
    """
    Genera un PDF con el certificado seleccionado.
    """
    certificado = get_object_or_404(Certificate.objects.select_related('usuario', 'program', 'empresa'), cert_code=cert_code)
    
    # Generar URL para el QR con un dominio personalizado
    # Puedes cambiarlo al dominio que prefieras, por ejemplo 'https://dampro.com.pe'
    custom_domain = 'https://rcmsolutionssac.com.pe'  # Cambia esto a tu dominio real
    verification_url = f"{custom_domain}/certificados/{cert_code}/"
    
    # Alternativamente, si prefieres seguir usando el dominio actual del servidor (desarrollo/producción):
    # verification_url = request.build_absolute_uri(
    #     reverse('system:certificado_detail', kwargs={'cert_code': cert_code})
    # )
    
    # Obtener el mes en español completo
    mes_numero = certificado.creation_date.month
    mes_espanol = get_mes_completo_espanol(mes_numero)
    
    # Generar QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    # Crear imagen del QR
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar imagen en memoria
    buffer = BytesIO()
    img.save(buffer)
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Renderizar el HTML
    html_string = render_to_string('system/certificado_pdf.html', {
        'certificado': certificado,
        'qr_code': qr_image_base64,
        'verification_url': verification_url,
        'mes_espanol': mes_espanol,
    })
    
    # Configuración de fuentes
    font_config = FontConfiguration()
    
    # Crear el PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    
    # Definir el nombre del archivo a descargar
    filename = f"certificado_{certificado.cert_code}.pdf"
    
    # Generar el PDF
    pdf = html.write_pdf(stylesheets=[], font_config=font_config)
    
    # Crear la respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def gestion_empresas(request):
    """
    Página para gestionar las empresas.
    Muestra todas las empresas registradas.
    """
    from django.core.paginator import Paginator
    
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    empresas_list = Empresa.objects.all()
    paginator = Paginator(empresas_list, 10)  # 10 empresas por página
    
    page_number = request.GET.get('page')
    empresas = paginator.get_page(page_number)
    
    return render(request, 'system/gestion_empresas.html', {
        'user': user,
        'empresas': empresas
    })

@login_required
def add_empresa(request):
    """
    Página para añadir una nueva empresa.
    """
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    error_message = None
    
    if request.method == 'POST':
        # Leer datos del formulario
        ruc = request.POST.get('ruc', '').strip()
        nombre = request.POST.get('nombre', '').strip()

        # Validar que no exista una empresa con el mismo RUC
        if Empresa.objects.filter(ruc=ruc).exists():
            error_message = f'Ya existe una empresa registrada con el RUC {ruc}. Por favor, verifique el número o busque la empresa en la lista.'
        else:
            try:
                # Crear y guardar
                Empresa.objects.create(
                    ruc=ruc,
                    nombre=nombre
                )
                return redirect('system:gestion_empresas')
            except Exception as e:
                error_message = 'Ocurrió un error al guardar la empresa. Por favor, intente nuevamente.'

    return render(request, 'system/empresa_form.html', {
        'user': user,
        'action': 'add',
        'empresa': None,
        'error_message': error_message
    })

def buscar_dni_view(request):
    """
    Vista para buscar información de DNI usando servicios externos
    """
    if request.method == 'POST':
        dni = request.POST.get('dni', '').strip()
        
        # Validar que el DNI tenga 8 dígitos
        if not dni or len(dni) != 8 or not dni.isdigit():
            return JsonResponse({'error': 'DNI inválido. Debe contener 8 dígitos numéricos.'}, status=400)

        # Intentar con el servicio principal
        try:
            url = 'https://eldni.com/pe/buscar-datos-por-dni'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Usar una sesión para mantener las cookies
            with requests.Session() as s:
                # 1. Obtener la página inicial y el token CSRF
                get_response = s.get(url, headers=headers, timeout=5)
                get_response.raise_for_status()
                
                soup = BeautifulSoup(get_response.text, 'html.parser')
                token_input = soup.find('input', {'name': '_token'})
                
                if not token_input:
                    # Si no se puede obtener el token, probar con el segundo servicio
                    raise ValueError('No se pudo encontrar el token de seguridad')
                
                token = token_input['value']

                # 2. Enviar la petición POST con el DNI y el token
                payload = {
                    'dni': dni,
                    '_token': token
                }
                post_response = s.post(url, data=payload, headers=headers, timeout=5)
                post_response.raise_for_status()

                # 3. Analizar la respuesta
                soup = BeautifulSoup(post_response.text, 'html.parser')
                table = soup.find('table', {'class': 'table table-striped table-scroll'})

                if table:
                    rows = table.find_all('tr')
                    if len(rows) > 1:
                        cols = rows[1].find_all('td')
                        nombres = cols[1].text.strip()
                        apellido_paterno = cols[2].text.strip()
                        apellido_materno = cols[3].text.strip()
                        
                        # Si encontramos datos, retornarlos
                        if nombres and apellido_paterno:
                            return JsonResponse({
                                'nombres': nombres,
                                'apellido_paterno': apellido_paterno,
                                'apellido_materno': apellido_materno
                            })
        except Exception as e:
            # Intentar con un servicio de respaldo
            try:
                # Esta URL es un ejemplo, reemplazar con una API real si está disponible
                url_backup = f'https://api.apis.net.pe/v1/dni?numero={dni}'
                response_backup = requests.get(url_backup, headers=headers, timeout=5)
                response_backup.raise_for_status()
                
                data_backup = response_backup.json()
                if data_backup and 'nombres' in data_backup:
                    return JsonResponse({
                        'nombres': data_backup.get('nombres', ''),
                        'apellido_paterno': data_backup.get('apellidoPaterno', ''),
                        'apellido_materno': data_backup.get('apellidoMaterno', '')
                    })
            except:
                pass
        
        # Si no se encontró en ningún servicio, mostrar mensaje informativo
        return JsonResponse({
            'error': f'No se encontraron datos para el DNI {dni}. Por favor ingrese los datos manualmente.'
        }, status=404)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def buscar_ruc_view(request):
    """
    Vista para buscar información de RUC - versión de demostración
    """
    if request.method == 'POST':
        ruc = request.POST.get('ruc', '').strip()
        
        # Validar que el RUC tenga 11 dígitos
        if not ruc or len(ruc) != 11 or not ruc.isdigit():
            return JsonResponse({'error': 'RUC inválido. Debe contener 11 dígitos numéricos.'}, status=400)

        # Base de datos de demostración con RUCs de empresas conocidas
        demo_rucs = {
            '20100017491': {
                'razon_social': 'TELEFONICA DEL PERU S.A.A.',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. AREQUIPA NRO. 1155 LIMA - LIMA - LIMA'
            },
            '20131312955': {
                'razon_social': 'SAGA FALABELLA S.A.',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. PASEO DE LA REPUBLICA NRO. 3220 LIMA - LIMA - SAN ISIDRO'
            },
            '20100070970': {
                'razon_social': 'SUPERMERCADOS PERUANOS SOCIEDAD ANONIMA',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. MORALES DUAREZ NRO. 1760 LIMA - LIMA - MIRAFLORES'
            },
            '20547121205': {
                'razon_social': 'RIPLEY CORP PERU S.A.',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. JAVIER PRADO ESTE NRO. 4200 LIMA - LIMA - SURCO'
            },
            '20100128056': {
                'razon_social': 'CORPORACION WONG S.A.',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. SANTA CRUZ NRO. 814 LIMA - LIMA - MIRAFLORES'
            },
            '20100000001': {
                'razon_social': 'EMPRESA DE PRUEBA S.A.C.',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. EJEMPLO NRO. 123 LIMA - LIMA - LIMA'
            }
        }

        # Simular delay de consulta para hacerlo más realista
        import time
        time.sleep(1)

        # Buscar en la base de datos de demostración
        if ruc in demo_rucs:
            empresa_data = demo_rucs[ruc]
            return JsonResponse({
                'ruc': ruc,
                'razon_social': empresa_data['razon_social'],
                'estado': empresa_data['estado'],
                'condicion': empresa_data['condicion'],
                'direccion': empresa_data['direccion']
            })
        else:
            # Para otros RUCs, intentar con API real si está disponible
            try:
                url = f'https://api.apis.net.pe/v1/ruc?numero={ruc}'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
                
                response = requests.get(url, headers=headers, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                if data and 'nombre' in data:
                    return JsonResponse({
                        'ruc': data.get('numeroDocumento', ruc),
                        'razon_social': data.get('nombre', ''),
                        'estado': data.get('estado', 'ACTIVO'),
                        'condicion': data.get('condicion', 'HABIDO'),
                        'direccion': data.get('direccion', ''),
                    })
            except:
                pass
            
            return JsonResponse({'error': f'No se encontraron datos para el RUC {ruc}. Intente con uno de los RUCs de prueba: 20100017491, 20131312955, 20100070970, 20547121205, 20100128056, 20100000001'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def edit_empresa(request, pk):
    """
    Página para editar una empresa existente.
    """
    # Obtener información del usuario logueado
    user = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
    
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        empresa.ruc = request.POST.get('ruc', empresa.ruc).strip()
        empresa.nombre = request.POST.get('nombre', empresa.nombre).strip()
        empresa.save()
        return redirect('system:gestion_empresas')

    return render(request, 'system/empresa_form.html', {
        'user': user,
        'action': 'edit',
        'empresa': empresa
    })

@login_required
def perfil_usuario(request):
    """
    Página de perfil del usuario logueado donde puede ver y editar su información.
    """
    user_account = UserAccount.objects.select_related('usuario', 'usuario__empresa').get(pk=request.session['user_id'])
    usuario = user_account.usuario
    
    return render(request, 'system/perfil_usuario.html', {
        'user_account': user_account,
        'usuario': usuario,
        'user': user_account  # Para mantener compatibilidad con templates existentes
    })

@csrf_exempt
@login_required
def actualizar_perfil(request):
    """
    API endpoint para actualizar los datos del perfil del usuario.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_account = UserAccount.objects.select_related('usuario').get(pk=request.session['user_id'])
            usuario = user_account.usuario
            
            campo = data.get('campo')
            valor = data.get('valor', '').strip()
            
            # Validar que el campo sea editable
            campos_editables = ['first_name', 'last_name', 'second_last_name', 'dni', 'username', 'password']
            
            if campo not in campos_editables:
                return JsonResponse({'error': 'Campo no editable'}, status=400)
            
            # Validaciones específicas
            if campo == 'dni':
                if len(valor) != 8 or not valor.isdigit():
                    return JsonResponse({'error': 'El DNI debe tener 8 dígitos'}, status=400)
                # Verificar que el DNI no esté en uso por otro usuario
                if Usuario.objects.filter(dni=valor).exclude(id=usuario.id).exists():
                    return JsonResponse({'error': 'Este DNI ya está en uso'}, status=400)
            
            if campo == 'username':
                if len(valor) < 3:
                    return JsonResponse({'error': 'El nombre de usuario debe tener al menos 3 caracteres'}, status=400)
                # Verificar que el username no esté en uso por otro usuario
                if UserAccount.objects.filter(username=valor).exclude(id=user_account.id).exists():
                    return JsonResponse({'error': 'Este nombre de usuario ya está en uso'}, status=400)
            
            if campo == 'password':
                if len(valor) < 6:
                    return JsonResponse({'error': 'La contraseña debe tener al menos 6 caracteres'}, status=400)
            
            if campo in ['first_name', 'last_name']:
                if len(valor) < 2:
                    return JsonResponse({'error': 'Este campo debe tener al menos 2 caracteres'}, status=400)
            
            # Actualizar el campo correspondiente
            if campo in ['first_name', 'last_name', 'second_last_name', 'dni']:
                setattr(usuario, campo, valor)
                usuario.save()
            elif campo in ['username', 'password']:
                setattr(user_account, campo, valor)
                user_account.save()
            
            return JsonResponse({'success': True, 'mensaje': 'Campo actualizado correctamente'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except UserAccount.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def api_buscar_usuarios(request):
    """
    API para buscar usuarios por nombre para autocompletado
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        
        # Si no hay query o es muy corto, devolver todos los usuarios (para mostrar lista completa)
        if len(query) < 2:
            usuarios = Usuario.objects.filter(
                user_type="Empleado"
            ).select_related('empresa')[:20]  # Limitar a 20 resultados para mostrar todos inicialmente
        else:
            # Buscar usuarios que coincidan con el query en nombre o apellido
            usuarios = Usuario.objects.filter(
                user_type="Empleado"
            ).filter(
                models.Q(first_name__icontains=query) |
                models.Q(last_name__icontains=query) |
                models.Q(second_last_name__icontains=query)
            ).select_related('empresa')[:10]  # Limitar a 10 resultados cuando se filtra
        
        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id,
                'nombre_completo': f"{usuario.first_name} {usuario.last_name}",
                'empresa': usuario.empresa.nombre if usuario.empresa else 'Sin empresa asignada',
                'texto_display': f"{usuario.first_name} {usuario.last_name}{' - ' + usuario.empresa.nombre if usuario.empresa else ' - Sin empresa asignada'}"
            })
        
        return JsonResponse({'usuarios': usuarios_data})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required 
def api_buscar_programas(request):
    """
    API para buscar programas por nombre para autocompletado
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        programas_qs = TrainingProgram.objects.all()
        if tipo:
            programas_qs = programas_qs.filter(program_type__iexact=tipo)
        if len(query) >= 2:
            programas_qs = programas_qs.filter(name__icontains=query)
            programas = programas_qs[:10]
        else:
            programas = programas_qs[:20]
        programas_data = []
        for programa in programas:
            programas_data.append({
                'id': programa.id,
                'name': programa.name,
                'hours': programa.hours,
                'program_type': programa.program_type,
                'texto_display': f"{programa.name} - {programa.program_type} ({programa.hours} horas)"
            })
        return JsonResponse({'programas': programas_data})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required 
def api_buscar_empresas(request):
    """
    API para buscar empresas por nombre o RUC para autocompletado
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        
        # Si no hay query o es muy corto, devolver todas las empresas (para mostrar lista completa)
        if len(query) < 2:
            empresas = Empresa.objects.all()[:20]  # Limitar a 20 resultados para mostrar todos inicialmente
        else:
            # Buscar empresas que coincidan con el query en nombre o RUC
            empresas = Empresa.objects.filter(
                models.Q(nombre__icontains=query) |
                models.Q(ruc__icontains=query)
            )[:10]  # Limitar a 10 resultados cuando se filtra
        
        empresas_data = []
        for empresa in empresas:
            empresas_data.append({
                'id': empresa.id,
                'nombre': empresa.nombre,
                'ruc': empresa.ruc,
                'texto_display': f"{empresa.nombre} - RUC: {empresa.ruc}"
            })
        
        return JsonResponse({'empresas': empresas_data})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)