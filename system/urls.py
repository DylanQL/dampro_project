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
    path('cursos/', views.cursos, name='cursos'),
    path('certificados/', views.certificados, name='certificados'),
    path('certificados/<str:cert_code>/', views.certificado_detail, name='certificado_detail'),
    path('certificados/pdf/<str:cert_code>/', views.certificado_pdf, name='certificado_pdf'),

    path('dashboard/usuarios/',       views.gestion_usuarios, name='gestion_usuarios'),
    path('dashboard/usuarios/add/',   views.add_usuario,      name='add_usuario'),
    path('dashboard/usuarios/edit/<int:pk>/', views.edit_usuario, name='edit_usuario'),

    path('dashboard/empresas/', views.gestion_empresas, name='gestion_empresas'),
    path('dashboard/empresas/add/', views.add_empresa, name='add_empresa'),
    path('dashboard/empresas/edit/<int:pk>/', views.edit_empresa, name='edit_empresa'),

    path('dashboard/cursos/', views.gestion_cursos,  name='gestion_cursos'),
    path('dashboard/cursos/add/', views.add_curso,       name='add_curso'),
    path('dashboard/cursos/edit/<int:pk>/', views.edit_curso,   name='edit_curso'),

    path('dashboard/certificados/', views.gestion_certificados, name='gestion_certificados'),
    path('dashboard/certificados/add/', views.add_certificado,      name='add_certificado'),
    path('dashboard/certificados/edit/<int:pk>/', views.edit_certificado,   name='edit_certificado'),

    path('api/buscar-dni/', views.buscar_dni_view, name='buscar_dni'),
    path('api/buscar-ruc/', views.buscar_ruc_view, name='buscar_ruc'),
]
