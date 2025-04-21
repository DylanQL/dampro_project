# system/urls.py
from django.urls import path
from . import views

app_name = "system"

urlpatterns = [
    path('', views.index, name='home'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('servicios/', views.servicios, name='servicios'),
    path('cursos/', views.cursos, name='cursos'),
    path('certificados/', views.certificados, name='certificados'),
    path('login/', views.login_view, name='login'),
]
