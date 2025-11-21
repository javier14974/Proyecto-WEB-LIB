from django import forms
from .models import *
from django.contrib.auth.models import User
import os
import magic 
import re

class registrarUsuario(forms.ModelForm):
    username = forms.CharField(label='nombre')
    password = forms.CharField(widget=forms.PasswordInput, label='contraseña')  #solo djgango no se reflejaran en la base de datos
    email = forms.CharField(label='correo')



    class Meta:
        model = Usuario
        fields = ['carrera', 'ciudad', 'universidad', 'edad', 'rol']

    field_order = ['username', 'password', 'email', 'carrera', 'ciudad', 'universidad', 'edad', 'rol'] #orden

    def clean(self):
        cleaned_data = super().clean()
        for campo in ['carrera', 'ciudad', 'universidad', 'edad', 'rol']:
            valor = cleaned_data.get(campo)
            if valor:
                cleaned_data[campo] = re.sub(r'[<>"]', '', valor) #letras proibidas
        return cleaned_data


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya existe.")
        return username

def save(self, commit=True):
    if not self.instance.pk:  # Solo si es creación
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )
        self.instance.user = user
    else:
        # Para edición, actualiza email si lo quieres
        self.instance.user.email = self.cleaned_data.get('email', self.instance.user.email)
        self.instance.user.save()
    
    usuario = super().save(commit=commit)
    return usuario








class subir_apuntes_forms(forms.ModelForm):
    class Meta:
        model = Apunte
        fields = ['titulo', 'descripcion', 'archivo', 'asignatura', 'carrera']

    def clean(self):
        cleaned_data = super().clean()
        for campo in ['titulo', 'descripcion', 'asignatura', 'carrera']:
            valor = cleaned_data.get(campo)
            if valor:
                cleaned_data[campo] = re.sub(r'[<>"]', '', valor) #letras proibidas
        return cleaned_data


    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo', False)
        if archivo:
            ext = os.path.splitext(archivo.name)[1].lower()  #optener extencion asi poder verificar si es pdf o otro archivo
            valid_extensions = ['.pdf', '.doc', '.docx']
            if ext not in valid_extensions:
                raise forms.ValidationError('Solo se permiten archivos PDF o Word (.doc, .docx)')
            
            mime = magic.from_buffer(archivo.read(1024), mime=True)
        archivo.seek(0)  # volver al inicio del archivo
        if mime not in ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            raise forms.ValidationError('El archivo no coincide con su extensión')
        
        return archivo


