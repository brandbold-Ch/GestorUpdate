from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.MaestrosLoginView.as_view(), name='maestros_login'),
    path('logout/', views.MaestrosLogoutView.as_view(), name='maestros_logout'),

    path('home/', views.MaestrosHomeView.as_view(), name='maestros_home'),
    path('credencial/', views.MaestrosCredencialView.as_view(), name='maestros_credencial'),

    path('perfil/', views.MaestrosPerfilView.as_view(), name='maestros_editar'),
    path('ficha_medica_contacto_emergencia', views.MaestrosFichaMedicaView.as_view(), name='maestros_ficha_medica_contacto_emergencia'),

    path('solicitud/', views.MaestroSolicitudCredencialView.as_view(), name='maestros_solicitud_credencial'),

    path('recuperar/', views.MaestroRestaurarPassword.as_view(), name='maestro_recuperar'),
    path('error/', views.ErrorView.as_view(), name='maestro_error'),
    path('aceptado/', views.AceptacionCambio.as_view(), name='maestro_aceptado'),

    path('crear/', views.MaestroCrearView.as_view(), name='maestros_crear'),
]
