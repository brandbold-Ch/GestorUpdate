from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.AlumnosLoginView.as_view(), name='alumnos_login'),
    path('logout/', views.AlumnosLogoutView.as_view(), name='alumnos_logout'),

    path('home/', views.AlumnosHomeView.as_view(), name='alumnos_home'),
    path('credencial/', views.AlumnosCredencialView.as_view(), name='alumnos_credencial'),
    path('perfil/', views.AlumnoPerfilView.as_view(), name='alumnos_editar'),

    path('ficha_medica_contacto_emergencia/', views.AlumnosFichaMedicaView.as_view(), name='alumnos_ficha_medica_contacto_emergencia'),

    path('solicitud/', views.AlumnoSolicituCredencialView.as_view(), name='alumnos_solicitud_credencial'),

    path('crear/', views.AlumnosCrearView.as_view(), name='alumnos_crear'),
]