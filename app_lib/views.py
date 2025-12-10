from django.shortcuts import render, get_object_or_404
from .forms import *
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Avg
from django.http import FileResponse, Http404
from django.core.paginator import Paginator






def agregar_usuario(request):
    if request.method == 'POST':
        form = registrarUsuario(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
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

    paginator = Paginator(apuntes, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "template/home.html", {
        "page_obj": page_obj,
        "apuntes": apuntes,
        "nombre": nombre,
        "asignatura": asignatura,
        "carrera": carrera,
    })



@login_required
def perfil_vista(request, usuario_id):
    # Obtener el usuario
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Apuntes propios
    apuntes = Apunte.objects.filter(usuario=usuario)

    # Apuntes compartidos a este usuario
    apuntes_compartidos = ApunteCompartido.objects.filter(usuario=usuario).select_related('apunte', 'apunte__usuario')

    return render(request, "template/perfil.html", {
        "apuntes": apuntes,
        "apuntes_compartidos": apuntes_compartidos,
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


def compartir_apunte(request, apunte_id):
    username = request.GET.get("username", "")

    apunte = get_object_or_404(Apunte, id=apunte_id)

    nombre_filtrado = Usuario.objects.filter(
        user__username__icontains=username
    ) if username else []

    return render(request, "template/compartir.html", {
        "username": username,
        "nombre_filtrado": nombre_filtrado,
        "apunte_actual": apunte,  # renombramos aquí
    })


@login_required
def hacer_compartido(request, apunte_id, usuario_id):
    apunte = get_object_or_404(Apunte, id=apunte_id)
    usuario_receptor = get_object_or_404(Usuario, id=usuario_id)

    compartido, creado = ApunteCompartido.objects.get_or_create(
            apunte=apunte,
            usuario=usuario_receptor
        )
    # Verificar si ya fue compartido
    if creado:
        messages.success(request, f"Apunte compartido correctamente con {usuario_receptor.user.username}.")
    else:
        messages.warning(request, f"El apunte ya estaba compartido con {usuario_receptor.user.username}.")

    return redirect("detalle_apunte", apunte_id=apunte.id)






@login_required
def eliminar_compartido(request, apunte_id):
    usuario = request.user.usuario  # tu modelo Usuario
    # Busca solo la relación compartida para este usuario
    compartido = ApunteCompartido.objects.filter(apunte_id=apunte_id, usuario=usuario).first()
    if compartido:
        compartido.delete()
    return redirect('perfil_vista', usuario_id=usuario.id)











def detalle_apunte(request, apunte_id):
    apunte = get_object_or_404(Apunte, id=apunte_id)
    promedio = ApunteCalificacion.objects.filter(apunte=apunte).aggregate(Avg("calificacion"))["calificacion__avg"] or 0

    usuario = None
    if request.user.is_authenticated:
        try:
            # Intenta acceder al perfil de usuario (Usuario)
            usuario = request.user.usuario 
        except Usuario.DoesNotExist:
            # Si el perfil no existe, 'usuario' se queda en None y no se usa para calificar/guardar.
            pass 


    if request.method == "POST" and usuario: 
        calificacion = request.POST.get("calificacion")
        ApunteCalificacion.objects.update_or_create(
            apunte=apunte,
            usuario=usuario, # Usamos la variable 'usuario' ya validada
            defaults={"calificacion": calificacion},
        )
        return redirect("detalle_apunte", apunte_id=apunte.id)
    
    return render(request, "template/detalle_apunte.html", {
        "apunte": apunte,
        "promedio": promedio,
        "usuario": usuario, # Pasamos la variable 'usuario' (puede ser None)
    })





def login_admin(request):
    form_admin = formulario_admin(request.POST or None)

    if request.method == "POST":
        if form_admin.is_valid():
            username = form_admin.cleaned_data['username']
            password = form_admin.cleaned_data['password']

            usuario = authenticate(request, username=username, password=password)

            if usuario is not None:
                if usuario.is_superuser:  #solo admin
                    login(request, usuario)
                    return redirect("admin_home")
                else:
                    # No es superusuario
                    return redirect("login")



    return render(request, "administrador/login_admin.html", {"formulario_admin": form_admin})

    
@login_required
@user_passes_test(lambda u: u.is_staff)  # solo super usuario
# Si esta es tu única vista de administrador:
def admin_home(request): # O llámala 'todos_usuarios' si la usas para ambas cosas
    apuntes = Apunte.objects.all()
    todos_los_usuarios = Usuario.objects.all() 
    return render(request, 'administrador/admin_home.html', {
        "apuntes": apuntes, 
        "todos_los_usuarios": todos_los_usuarios
    })




@user_passes_test(lambda u: u.is_superuser) 
def todos_usuarios(request):
    # 1. Obtener el parámetro de búsqueda
    username_query = request.GET.get("username", "")

    # 2. Filtrar los usuarios: si hay query, filtra; si no, trae todos.
    if username_query:
        # 🔑 Si el filtro sigue sin funcionar, revisa que 'user__username__icontains'
        #    sea la manera correcta de acceder al nombre de usuario
        todos_los_usuarios = Usuario.objects.filter(
            user__username__icontains=username_query
        )
    else:
        # Esto asegura que aparezcan todos por defecto
        todos_los_usuarios = Usuario.objects.all() 
        
    # 3. Obtener todos los apuntes (necesario para la otra sección de la plantilla)
    apuntes = Apunte.objects.all()
        
    return render(request, 'administrador/admin_home.html', {
        "todos_los_usuarios": todos_los_usuarios,
        "username_query": username_query,
        "apuntes": apuntes # ⬅️ Agregado para cargar la sección de apuntes
    })

@user_passes_test(lambda u: u.is_superuser) 
def eliminar_usuario(request, usuario_id):
    perfil_usuario = get_object_or_404(Usuario, id=usuario_id)
    
    usuario_django = perfil_usuario.user #eliminar por completo al usuario 
    
    usuario_django.delete()
    
    
    return redirect('todos_usuarios')
