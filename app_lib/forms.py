from django import forms
from .models import *
from django.contrib.auth.models import User
import zipfile, re, magic, os
from .validation import validar_no_numeros
from .validation import validar_solo_letras_y_num
from .validation import validar_solo_letras




class registrarUsuario(forms.ModelForm):

    username = forms.CharField(
        label='Nombre',
        min_length=3,
        max_length=40,
        required=True,
        error_messages={
            "required": "El nombre es obligatorio.",
            "min_length": "El nombre debe tener al menos 3 caracteres.",
            "max_length": "El nombre no debe superar los 40 caracteres."
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label='contraseña',
        required=True,
        min_length=3,
        max_length=9,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "min_length": "Debe tener mínimo 3 caracteres.",
            "max_length": "No puede superar los 9 caracteres."
        }
    )

    email = forms.EmailField(
        label='correo',
        required=True,
        error_messages={
            "required": "El correo es obligatorio.",
            "invalid": "Debes ingresar un correo válido."
        }
    )

    carrera = forms.CharField(
        required=True,
        min_length=3,
        max_length=25,
        validators=[validar_no_numeros],
        error_messages={
            "required": "La carrera es obligatoria.",
            "min_length": "Debe tener mínimo 3 caracteres.",
            "max_length": "No puede superar los 25 caracteres."
        }
    )

    ciudad = forms.CharField(
        required=True,
        min_length=3,
        max_length=25,
        validators=[validar_no_numeros],
        error_messages={
            "required": "La ciudad es obligatoria.",
            "min_length": "Debe tener mínimo 3 caracteres.",
            "max_length": "No puede superar los 25 caracteres."
        }
    )

    universidad = forms.CharField(
        required=True,
        min_length=3,
        max_length=25,
        validators=[validar_no_numeros],
        error_messages={
            "required": "La universidad es obligatoria.",
            "min_length": "Debe tener mínimo 3 caracteres.",
            "max_length": "No puede superar los 25 caracteres."
        }
    )

    edad = forms.IntegerField(
        required=True,
        min_value=1,     
        max_value=100,   
        error_messages={
            "required": "La edad es obligatoria.",
            "invalid": "Debes ingresar un número válido.",
            "min_value": "La edad no puede ser menor a 1.",
            "max_value": "La edad no puede ser mayor a 100."
        }
    )

    class Meta:
        model = Usuario
        fields = ['carrera', 'ciudad', 'universidad', 'edad', 'rol']

    field_order = [
        'username', 'password', 'email',
        'carrera', 'ciudad', 'universidad', 'edad', 'rol'
    ]


    
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya existe.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:
            email = email.lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        for campo in ['carrera', 'ciudad', 'universidad', 'rol']:
            valor = cleaned_data.get(campo)

            if not valor:
                raise forms.ValidationError(f"El campo '{campo}' es obligatorio.")

            if isinstance(valor, str):
                valor = valor.strip()
                

                validar_solo_letras(valor)

                cleaned_data[campo] = valor

        edad = cleaned_data.get("edad")
        if edad is None:
            raise forms.ValidationError("La edad es obligatoria.")
        if edad < 1 or edad > 100:
            raise forms.ValidationError("La edad debe estar entre 1 y 100.")

        return cleaned_data


    def save(self, commit=True):
        if not self.instance.pk:  # Solo si se está creando
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
            )
            self.instance.user = user
        else:
            self.instance.user.email = self.cleaned_data.get('email', self.instance.user.email)
            self.instance.user.save()

        usuario = super().save(commit=commit)
        return usuario




class subir_apuntes_forms(forms.ModelForm):

    titulo = forms.CharField(
        required=True,
        min_length=3,
        max_length=40,
        validators=[validar_solo_letras_y_num],
        error_messages={
            "required": "El título es obligatorio.",
            "min_length": "El título debe tener mínimo 3 caracteres.",
            "max_length": "El título no puede superar los 40 caracteres.",
            "invalid": "El título solo puede contener letras, números y espacios."
        }
    )

    descripcion = forms.CharField(
        required=True,
        min_length=10,
        max_length=100,
        widget=forms.Textarea,
        error_messages={
            "required": "La descripción es obligatoria.",
            "min_length": "La descripción debe tener mínimo 10 caracteres.",
            "max_length": "La descripción no puede superar 100 caracteres."
        }
    )

    asignatura = forms.CharField(
        required=True,
        min_length=3,
        max_length=40,
        validators=[validar_no_numeros],
        error_messages={
            "required": "La asignatura es obligatoria.",
            "min_length": "Debe tener mínimo 3 caracteres.",
            "max_length": "No puede superar 40 caracteres.",
            "invalid": "La asignatura solo puede contener letras y espacios."
        }
    )

    carrera = forms.CharField(
        required=True,
        min_length=3,
        max_length=30,
        validators=[validar_no_numeros],
        error_messages={
            "required": "La carrera es obligatoria.",
            "min_length": "Debe tener mínimo 3 caracteres.",
            "max_length": "No puede superar 30 caracteres.",
            "invalid": "La carrera solo puede contener letras y espacios."
        }
    )

    class Meta:
        model = Apunte
        fields = ['titulo', 'descripcion', 'archivo', 'asignatura', 'carrera']



    def clean(self):
        cleaned_data = super().clean()

        for campo in ['titulo', 'descripcion', 'asignatura', 'carrera']:

            valor = cleaned_data.get(campo)
            if not valor:
                raise forms.ValidationError(f"El campo '{campo}' es obligatorio.")

            # Limpia espacios y caracteres peligrosos
            valor = valor.strip()
            valor = re.sub(r'[<>"]', '', valor)

            cleaned_data[campo] = valor

        return cleaned_data



    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo', False)

        if not archivo:
            return archivo

        max_size = 200 * 1024 * 1024  # 200 MB
        if archivo.size > max_size:
            raise forms.ValidationError("El archivo no puede superar los 200 MB.")

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
                    if not any(item.startswith("word/") for item in contenido):
                        raise forms.ValidationError("El archivo DOCX no es válido.")
            except zipfile.BadZipFile:
                raise forms.ValidationError("El archivo DOCX está corrupto o no es válido.")
        else:
            if mime not in valid_mime:
                raise forms.ValidationError("El archivo no coincide con su extensión.")

        return archivo


class formulario_admin(forms.Form):
    username = forms.CharField(error_messages={"required": "El nombre es obligatorio."})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={"required": "La contraseña es obligatoria."})



