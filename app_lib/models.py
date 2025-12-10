from django.db import models
from django.contrib.auth.models import User
import os
from django.utils.text import slugify

# Create your models here.


class Usuario(models.Model): #alumno/docente
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    carrera = models.CharField(max_length=50, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    universidad = models.CharField(max_length=100, null=True, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True) #automatica

    ROL_CHOICES = [   #rol obligatorio entre uno o otro
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    def __str__(self):
        return self.user.username  #al llamar a usuario se mostrar el nombre de este 



def ruta_subida_apuntes(instance, filename):
    email = instance.usuario.user.email
    safe_email = slugify(email)              # convierte el email en algo seguro
    safe_filename = slugify(os.path.splitext(filename)[0]) + os.path.splitext(filename)[1]
    return f"apuntes/{safe_email}/{safe_filename}"

def ruta_subida_imagen(instance, filename):
    email = instance.usuario.user.email
    safe_email = slugify(email)
    safe_filename = slugify(os.path.splitext(filename)[0]) + os.path.splitext(filename)[1]
    return f"apuntes/{safe_email}/imagenes/{safe_filename}"



class Apunte(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  

    titulo = models.CharField(max_length=40)
    descripcion = models.TextField(blank=True, null=True, max_length=100)
    carrera = models.TextField(blank=True, null=True, max_length=30)
    asignatura = models.TextField(blank=True, null=True, max_length=40)
    archivo = models.FileField(upload_to=ruta_subida_apuntes)
    imagen = models.ImageField(upload_to=ruta_subida_imagen, default="default_apunte.jpg")
    fecha_subida = models.DateTimeField(auto_now_add=True)




class ApunteCompartido(models.Model):
    apunte = models.ForeignKey(Apunte, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que recibe el apunte
    fecha_compartido = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('apunte', 'usuario')  # evita compartir dos veces con la misma persona

    def __str__(self):
        return f"{self.apunte.titulo} → {self.usuario.user.username}"



class ApunteCalificacion(models.Model):
    apunte = models.ForeignKey(Apunte, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calificacion = models.PositiveIntegerField()  # 1 a 5
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('apunte', 'usuario')  # solo puede calificar una ves

    def __str__(self):
        return f"{self.usuario.user.username} califica {self.apunte.titulo}: {self.calificacion}"
