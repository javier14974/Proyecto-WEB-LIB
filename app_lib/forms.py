from django import forms
from .models import *
from django.contrib.auth.models import User
import zipfile, re, magic, os

class registrarUsuario(forms.ModelForm):
    username = forms.CharField(label='nombre')
    password = forms.CharField(widget=forms.PasswordInput, label='contraseña')
    email = forms.CharField(label='correo')

    class Meta:
        model = Usuario
        fields = ['carrera', 'ciudad', 'universidad', 'edad', 'rol']

    field_order = ['username', 'password', 'email', 'carrera', 'ciudad', 'universidad', 'edad', 'rol']


    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya existe.")

        return username

    def clean(self):
        cleaned_data = super().clean()

        for campo in ['carrera', 'ciudad', 'universidad', 'rol']:
            valor = cleaned_data.get(campo)
            if isinstance(valor, str):
                cleaned_data[campo] = valor.strip()

        return cleaned_data





    def save(self, commit=True):
        if not self.instance.pk:  # Solo si se está creando
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
            )
            self.instance.user = user  # asigna el User creado
        else:
            # Para edición
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

            if not archivo:
                return archivo

            #maximo de tamaño de archivo
            max_size = 200 * 1024 * 1024  # 200 MB
            if archivo.size > max_size:
                raise forms.ValidationError("El archivo no puede superar los 200 MB.")

                #validacion de la extencuion del archivo
            ext = os.path.splitext(archivo.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx']
            if ext not in valid_extensions:
                raise forms.ValidationError("Solo se permiten archivos PDF o Word (.doc, .docx).")

            mime = magic.from_buffer(archivo.read(2048), mime=True)
            archivo.seek(0)

            valid_mime = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]

            
            if ext == '.docx':
                if mime not in valid_mime and not mime.startswith('application/zip'):
                    raise forms.ValidationError("El archivo DOCX no tiene un formato válido.")

             
                try:
                    with zipfile.ZipFile(archivo, 'r') as z:
                        contenido = z.namelist()
                        # Un DOCX válido SIEMPRE contiene "word/"
                        if not any(item.startswith("word/") for item in contenido):
                            raise forms.ValidationError("El archivo DOCX no es válido.")
                except zipfile.BadZipFile:
                    raise forms.ValidationError("El archivo DOCX está corrupto o no es válido.")

            else:
            
                if mime not in valid_mime:
                    raise forms.ValidationError("El archivo no coincide con su extensión.")

            return archivo
