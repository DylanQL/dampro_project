from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.urls import reverse
from functools import wraps
from .models import *
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

def cursos(request):
    return render(request, 'system/cursos.html')

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
    
    try:
        certificado = Certificate.objects.select_related('usuario', 'course', 'empresa').get(cert_code=cert_code)
    except Certificate.DoesNotExist:
        error = f"No se encontró ningún certificado con el código: {cert_code}"
    
    return render(request, 'system/certificado_detail.html', {
        'certificado': certificado,
        'error': error
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
    usuarios_count = Usuario.objects.count()
    empresas_count = Empresa.objects.count()
    cursos_count = Course.objects.count()
    certificados_count = Certificate.objects.count()
    
    return render(request, 'system/home_logged.html', {
        'user': user,
        'usuarios_count': usuarios_count,
        'empresas_count': empresas_count,
        'cursos_count': cursos_count,
        'certificados_count': certificados_count
    })

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
        last = request.POST.get('last_name', '').strip()
        second_last = request.POST.get('second_last_name', '').strip() or None
        dni = request.POST.get('dni', '').strip() or None
        utype = "Empleado"
        empresa_id = request.POST.get('empresa_id', '')

        # Comprobar si el DNI ya existe
        if dni and Usuario.objects.filter(dni=dni).exists():
            empresas = Empresa.objects.all()
            return render(request, 'system/usuario_form.html', {
                'action': 'add',
                'usuario': None,
                'empresas': empresas,
                'error_message': 'El DNI ingresado ya se encuentra registrado.'
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
            dni=dni,
            user_type=utype,
            empresa=empresa
        )
        return redirect('system:gestion_usuarios')
    
    empresas = Empresa.objects.all()
    return render(request, 'system/usuario_form.html', {
        'action': 'add',
        'usuario': None,
        'empresas': empresas
    })

@login_required
def edit_usuario(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    if request.method == 'POST':
        usuario.first_name       = request.POST.get('first_name', usuario.first_name).strip()
        usuario.last_name        = request.POST.get('last_name', usuario.last_name).strip()
        usuario.second_last_name = request.POST.get('second_last_name', usuario.second_last_name).strip() or None
        usuario.dni              = request.POST.get('dni', usuario.dni).strip() or None
        usuario.user_type        = request.POST.get('user_type', usuario.user_type).strip()
        
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
        'action': 'edit',
        'usuario': usuario,
        'empresas': empresas
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


@login_required
def gestion_certificados(request):
    certificados = Certificate.objects.select_related('usuario', 'course', 'empresa').all()
    return render(request, 'system/gestion_certificados.html', {
        'certificados': certificados
    })

@login_required
def add_certificado(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        course_id  = request.POST.get('course_id')
        horas      = request.POST.get('chronological_hours', '0').strip() or '0'

        usuario = get_object_or_404(Usuario, pk=int(usuario_id))
        course  = get_object_or_404(Course,  pk=int(course_id))

        # Generar un código aleatorio único para el certificado
        cert_code = generate_unique_cert_code()
        
        # Obtener automáticamente la empresa del usuario
        empresa = usuario.empresa
        
        # Crear el certificado con la fecha automática y la empresa del usuario
        Certificate.objects.create(
            usuario=usuario,
            course=course,
            empresa=empresa,
            chronological_hours=int(horas),
            cert_code=cert_code
        )
        return redirect('system:gestion_certificados')

    usuarios = Usuario.objects.all()
    cursos   = Course.objects.all()
    empresas = Empresa.objects.all()
    return render(request, 'system/certificado_form.html', {
        'action': 'add',
        'certificado': None,
        'usuarios': usuarios,
        'cursos': cursos,
        'empresas': empresas,
    })

@login_required
def edit_certificado(request, pk):
    certificado = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        course_id  = request.POST.get('course_id')
        empresa_id = request.POST.get('empresa_id')
        horas      = request.POST.get('chronological_hours', certificado.chronological_hours)
        creation_date = request.POST.get('creation_date')

        usuario = get_object_or_404(Usuario, pk=int(usuario_id))
        certificado.usuario = usuario
        certificado.course = get_object_or_404(Course, pk=int(course_id))
        
        # Permitir la selección manual de la empresa
        if empresa_id:
            try:
                certificado.empresa = get_object_or_404(Empresa, pk=int(empresa_id))
            except (ValueError, Empresa.DoesNotExist):
                certificado.empresa = None
        else:
            certificado.empresa = None
        
        certificado.chronological_hours = int(horas)
        
        # Actualizar la fecha si se proporcionó una nueva
        if creation_date:
            from datetime import datetime
            # Convertir la cadena de fecha-hora en un objeto datetime
            # El formato debe ser compatible con el formato datetime-local de HTML5
            try:
                certificado.creation_date = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M')
            except ValueError:
                # Si hay un problema con el formato, mantenemos la fecha actual
                pass
                
        certificado.save()
        return redirect('system:gestion_certificados')

    usuarios = Usuario.objects.all()
    cursos   = Course.objects.all()
    empresas = Empresa.objects.all()
    return render(request, 'system/certificado_form.html', {
        'action': 'edit',
        'certificado': certificado,
        'usuarios': usuarios,
        'cursos': cursos,
        'empresas': empresas,
    })

@login_required
def certificado_pdf(request, cert_code):
    """
    Genera un PDF con el certificado seleccionado.
    """
    certificado = get_object_or_404(Certificate.objects.select_related('usuario', 'course', 'empresa'), cert_code=cert_code)
    
    # Generar URL para el QR con un dominio personalizado
    # Puedes cambiarlo al dominio que prefieras, por ejemplo 'https://dampro.com.pe'
    custom_domain = 'http://localhost:8000'  # Cambia esto a tu dominio real
    verification_url = f"{custom_domain}/certificados/{cert_code}/"
    
    # Alternativamente, si prefieres seguir usando el dominio actual del servidor (desarrollo/producción):
    # verification_url = request.build_absolute_uri(
    #     reverse('system:certificado_detail', kwargs={'cert_code': cert_code})
    # )
    
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
    empresas = Empresa.objects.all()
    return render(request, 'system/gestion_empresas.html', {
        'empresas': empresas
    })

@login_required
def add_empresa(request):
    """
    Página para añadir una nueva empresa.
    """
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
        'action': 'add',
        'empresa': None,
        'error_message': error_message
    })

def buscar_dni_view(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        if not dni or len(dni) != 8:
            return JsonResponse({'error': 'DNI inválido'}, status=400)

        url = 'https://eldni.com/pe/buscar-datos-por-dni'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            # Usar una sesión para mantener las cookies
            with requests.Session() as s:
                # 1. Obtener la página inicial y el token CSRF
                get_response = s.get(url, headers=headers)
                get_response.raise_for_status()
                
                soup = BeautifulSoup(get_response.text, 'html.parser')
                token_input = soup.find('input', {'name': '_token'})
                
                if not token_input:
                    return JsonResponse({'error': 'No se pudo encontrar el token de seguridad.'}, status=500)
                
                token = token_input['value']

                # 2. Enviar la petición POST con el DNI y el token
                payload = {
                    'dni': dni,
                    '_token': token
                }
                post_response = s.post(url, data=payload, headers=headers)
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
                        
                        return JsonResponse({
                            'nombres': nombres,
                            'apellido_paterno': apellido_paterno,
                            'apellido_materno': apellido_materno
                        })

                return JsonResponse({'error': 'No se encontraron datos para el DNI ingresado.'}, status=404)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Error de conexión: {e}'}, status=500)

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
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        empresa.ruc = request.POST.get('ruc', empresa.ruc).strip()
        empresa.nombre = request.POST.get('nombre', empresa.nombre).strip()
        empresa.save()
        return redirect('system:gestion_empresas')

    return render(request, 'system/empresa_form.html', {
        'action': 'edit',
        'empresa': empresa
    })