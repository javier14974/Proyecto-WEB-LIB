from django.core.exceptions import ValidationError
import re

def validar_no_numeros(valor):
    if re.search(r'\d', valor):
        raise ValidationError("Este campo no puede contener números.")


def validar_solo_letras_y_num(value):
    pattern = re.compile(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$')
    if not pattern.match(value):
        raise ValidationError("Solo puede contener letras, números y espacios.")

def validar_solo_letras(value):
    pattern = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$')
    if not pattern.match(value):
        raise ValidationError("Solo puede contener letras y espacios.")