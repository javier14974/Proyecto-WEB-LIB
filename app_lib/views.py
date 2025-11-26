from django.shortcuts import render, get_object_or_404
from .forms import *
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Avg
from django.http import FileResponse, Http404

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    
    return render(request, 'login.html')


# Create your views here.

def home(request):
    apuntes = Apunte.objects.all()  # todos los apuntes
    return render(request, 'template/home.html', {'apuntes': apuntes})


def agregar_usuario(request):
    if request.method == 'POST':
        form = registrarUsuario(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = registrarUsuario()

    return render(request, 'template/agregar_usuario.html', {'form': form})



@login_required
def subir_apunte(request):
    if request.method == 'POST':
        form = subir_apuntes_forms(request.POST, request.FILES)
        if form.is_valid():
            apunte = form.save(commit=False)
            apunte.usuario = request.user.usuario  # asigna el usuario logiado
            apunte.save()
            return redirect('home')
    else:
        form = subir_apuntes_forms()

    return render(request, 'template/subir_apunte.html', {'form': form})


def login_vista(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    
    return render(request, 'template/login.html')


def logout_vista(request):
    logout(request)
    return redirect('login')





def detalle_apunte(request, apunte_id):
    apunte = get_object_or_404(Apunte, id=apunte_id)

    # Si hay calificación
    promedio = ApunteCalificacion.objects.filter(apunte=apunte).aggregate(Avg("calificacion"))["calificacion__avg"] or 0

    usuario = None
    if request.user.is_authenticated:
        usuario = request.user.usuario

    # Guardar calificación
    if request.method == "POST" and request.user.is_authenticated:
        calificacion = request.POST.get("calificacion")
        ApunteCalificacion.objects.update_or_create(
            apunte=apunte,
            usuario=request.user.usuario,
            defaults={"calificacion": calificacion},
        )
        return redirect("detalle_apunte", apunte_id=apunte.id)
    return render(request, "template/detalle_apunte.html", {
        "apunte": apunte,
        "promedio": promedio,
        "usuario": usuario,
    })


def pdf_apunte(request, apunte_id):
    apunte = get_object_or_404(Apunte, id=apunte_id)

    ruta = apunte.archivo.path
    response = FileResponse(open(ruta, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(ruta)}"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def home(request): #filtro
    apuntes = Apunte.objects.all()

    # filtros
    nombre = request.GET.get("nombre", "")
    asignatura = request.GET.get("asignatura", "")
    carrera = request.GET.get("carrera", "")

    if nombre:
        apuntes = apuntes.filter(titulo__icontains=nombre)

    if asignatura:
        apuntes = apuntes.filter(asignatura__icontains=asignatura)

    if carrera:
        apuntes = apuntes.filter(carrera__icontains=carrera)

    return render(request, "template/home.html", {
        "apuntes": apuntes,
        "nombre": nombre,
        "asignatura": asignatura,
        "carrera": carrera,
    })



@login_required
def perfil_vista(request, usuario_id):
    # Obtener el usuario
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Traer solo sus apuntes
    apuntes = Apunte.objects.filter(usuario=usuario)

    return render(request, "template/perfil.html", {
        "apuntes": apuntes,
        "usuario": usuario,
    })





@login_required
def eliminar_apunte(request, apunte_id):
    apunte = get_object_or_404(Apunte, id=apunte_id)
    apunte.delete()
    return redirect('home')


@login_required
def editar_apunte(request, apunte_id):
    # Obtener el docente a editar
    apunte = get_object_or_404(Apunte, id=apunte_id)

    # Crear el formulario pasando la instancia existente
    form = subir_apuntes_forms(request.POST or None, instance=apunte)

    if form.is_valid():
        form.save()  # Sobrescribe los datos existentes
        return redirect('home')  

    return render(request, 'template/subir_apunte.html', {'form': form, 'editar': True})



def nosotros(request):
    return render(request, "template/nosotros.html")