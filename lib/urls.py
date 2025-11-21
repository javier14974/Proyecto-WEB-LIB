"""
URL configuration for lib project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_lib.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('agregarUsuario/', agregar_usuario, name="agregar_usuario"),
    path('subir_apunte/', subir_apunte, name="subir_apunte"),
    path('login/', login_vista, name="login"),
    path('logout/', logout_vista, name='logout'),
    path('apunte/<int:apunte_id>/', detalle_apunte, name='detalle_apunte'),
    path('perfil/<int:usuario_id>/', perfil_vista, name='perfil_vista'),
    path('eliminar_apunte/<int:apunte_id>',eliminar_apunte, name='eliminar_apunte'),
    path('editar_apunte/<int:apunte_id>',editar_apunte, name='editar_apunte'),
    path("apunte/<int:apunte_id>/pdf/", pdf_apunte, name="pdf_apunte"),
    path("nosotros/", nosotros, name="nosotros"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))