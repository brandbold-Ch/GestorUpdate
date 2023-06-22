from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.AdministradoresLoginView.as_view(), name='administradores_login'),
    path('logout/', views.AdministradoresLogoutView.as_view(), name='administradores_logout'),

    path('home/', views.AdministradoresHomeView.as_view(), name='administradores_home'),
    path('credencial/', views.AdministradoresCredencialView.as_view(), name='administradores_credencial'),

    path('crear/', views.AdministradoresCrearView.as_view(), name='administradores_crear'),
]