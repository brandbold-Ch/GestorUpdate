from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('alumnos/', include('alumnos.urls')),
    path('administradores/', include('administradores.urls')),
    path('directivos/', include('directivos.urls')),
    path('maestros/', include('maestros.urls')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

handler404 = 'core.views.error_404'

