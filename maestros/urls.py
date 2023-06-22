from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.MaestrosLoginView.as_view(), name='maestros_login'),
    path('logout/', views.MaestrosLogoutView.as_view(), name='maestros_logout'),

    path('home/', views.MaestrosHomeView.as_view(), name='maestros_home'),
    path('credencial/', views.MaestrosCredencialView.as_view(), name='maestros_credencial'),

    path('perfil/', views.MaestrosPerfilView.as_view(), name='maestros_editar'),
    path('ficha_medica_contacto_emergencia', views.MaestrosFichaMedicaView.as_view(), name='maestros_ficha_medica_contacto_emergencia'),

    path('crear/', views.MaestroCrearView.as_view(), name='maestros_crear'),
]
