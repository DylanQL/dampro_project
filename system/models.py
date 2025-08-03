from django.db import models

# Create your models here.

class Empresa(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    nombre = models.CharField(max_length=200)  # razón social

class Usuario(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    second_last_name = models.CharField(max_length=100, blank=True, null=True)
    numero_documento = models.CharField(max_length=12, unique=True, null=True, blank=True)  # Número de documento (DNI o CE)
    tipo_documento = models.CharField(max_length=20, null=True)  # Tipo de documento
    user_type = models.CharField(max_length=50)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)

class UserAccount(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) # Esto luego lo encriptaremos
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='account')
    status = models.CharField(max_length=20)

class TrainingProgram(models.Model):
    name = models.CharField(max_length=200)
    hours = models.PositiveIntegerField()
    program_type = models.CharField(max_length=100)

class Certificate(models.Model):
    cert_code = models.CharField(max_length=100, unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='certificates')
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='certificates', null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    creation_date = models.DateTimeField(default=models.functions.Now)  # Se cambió de auto_now_add=True para permitir edición
    completion_date = models.DateTimeField(null=True, blank=True)  # Fecha de culminación (opcional)
    chronological_hours = models.PositiveIntegerField()
    modality = models.CharField(max_length=50, null=True)