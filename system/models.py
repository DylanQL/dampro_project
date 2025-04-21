from django.db import models

# Create your models here.

class Usuario(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    second_last_name = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=50)

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
    creation_date = models.DateTimeField(auto_now_add=True)
    chronological_hours = models.PositiveIntegerField()