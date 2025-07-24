# system/urls.py
from django.urls import path
from . import views

app_name = "system"

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.home_logged, name='home_logged'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('servicios/', views.servicios, name='servicios'),
    path('programas/', views.programas, name='programas'),
    path('certificados/', views.certificados, name='certificados'),
    path('certificados/<str:cert_code>/', views.certificado_detail, name='certificado_detail'),
    path('certificados/pdf/<str:cert_code>/', views.certificado_pdf, name='certificado_pdf'),

    path('dashboard/usuarios/',       views.gestion_usuarios, name='gestion_usuarios'),
    path('dashboard/usuarios/add/',   views.add_usuario,      name='add_usuario'),
    path('dashboard/usuarios/edit/<int:pk>/', views.edit_usuario, name='edit_usuario'),

    path('dashboard/empresas/', views.gestion_empresas, name='gestion_empresas'),
    path('dashboard/empresas/add/', views.add_empresa, name='add_empresa'),
    path('dashboard/empresas/edit/<int:pk>/', views.edit_empresa, name='edit_empresa'),

    path('dashboard/programas/', views.gestion_programas,  name='gestion_programas'),
    path('dashboard/programas/add/', views.add_programa,       name='add_programa'),
    path('dashboard/programas/edit/<int:pk>/', views.edit_programa,   name='edit_programa'),

    path('dashboard/certificados/', views.gestion_certificados, name='gestion_certificados'),
    path('dashboard/certificados/add/', views.add_certificado,      name='add_certificado'),
    path('dashboard/certificados/edit/<int:pk>/', views.edit_certificado,   name='edit_certificado'),

    path('dashboard/perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('api/actualizar-perfil/', views.actualizar_perfil, name='actualizar_perfil'),
    
    path('api/buscar-dni/', views.buscar_dni_view, name='buscar_dni'),
    path('api/buscar-ruc/', views.buscar_ruc_view, name='buscar_ruc'),
    path('api/buscar-usuarios/', views.api_buscar_usuarios, name='api_buscar_usuarios'),
    path('api/buscar-programas/', views.api_buscar_programas, name='api_buscar_programas'),
    path('api/buscar-empresas/', views.api_buscar_empresas, name='api_buscar_empresas'),
]
