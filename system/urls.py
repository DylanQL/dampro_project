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

    path('dashboard/usuarios/',       views.gestion_usuarios, name='gestion_usuarios'),
    path('dashboard/usuarios/add/',   views.add_usuario,      name='add_usuario'),
    path('dashboard/usuarios/edit/<int:pk>/', views.edit_usuario, name='edit_usuario'),

    path('dashboard/cursos/', views.gestion_cursos,  name='gestion_cursos'),
    path('dashboard/cursos/add/', views.add_curso,       name='add_curso'),
    path('dashboard/cursos/edit/<int:pk>/', views.edit_curso,   name='edit_curso'),

]
