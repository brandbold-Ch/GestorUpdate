from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.AdministradoresLoginView.as_view(), name='administradores_login'),
    path('logout/', views.AdministradoresLogoutView.as_view(), name='administradores_logout'),

    path('home/', views.AdministradoresHomeView.as_view(), name='administradores_home'),
    path('credencial/', views.AdministradoresCredencialView.as_view(), name='administradores_credencial'),
    path('perfil/', views.AdministradoresEditarView.as_view(), name='administradores_editar'),

    path('ficha_medica_contacto_emergencia/', views.AdministradoresFichaMedicaView.as_view(), name='administradores_ficha_medica_contacto_emergencia'),

    path('crear/', views.AdministradoresCrearView.as_view(), name='administradores_crear'),
]