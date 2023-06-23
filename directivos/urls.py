from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.DirectivosLoginView.as_view(), name='directivos_login'),
    path('logout/', views.DirectivosLogoutView.as_view(), name='directivos_logout'),

    path('home/', views.DirectivosHomeView.as_view(), name='directivos_home'),
    path('credencial/', views.DirectivosCredencialView.as_view(), name='directivos_credencial'),

    path('perfil/', views.DirectivosPerfilView.as_view(), name='directivos_editar'),
    path('ficha_medica_contacto_emergencia/', views.DirectivoFichaMedicaView.as_view(), name='directivos_ficha_medica'),

    path('solicitud/', views.DirectivoSolicitudCredencialView.as_view(), name='directivos_solicitud_credencial'),

    path('crear/', views.DirectivosCrearView.as_view(), name='directivos_crear'),
]