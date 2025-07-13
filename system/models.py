from django.db import models

# Create your models here.

class Empresa(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    nombre = models.CharField(max_length=200)  # razón social

class Usuario(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    second_last_name = models.CharField(max_length=100, blank=True, null=True)
    dni = models.CharField(max_length=8, unique=True, null=True, blank=True)  # DNI peruano estándar de 8 dígitos
    user_type = models.CharField(max_length=50)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)

class UserAccount(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) # Esto luego lo encriptaremos
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='account')
    status = models.CharField(max_length=20)

class Course(models.Model):
    name = models.CharField(max_length=200)
    course_hours = models.PositiveIntegerField()

class Certificate(models.Model):
    cert_code = models.CharField(max_length=100, unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    creation_date = models.DateTimeField(default=models.functions.Now)  # Se cambió de auto_now_add=True para permitir edición
    chronological_hours = models.PositiveIntegerField()