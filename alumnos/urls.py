from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.AlumnosLoginView.as_view(), name='alumnos_login'),
    path('logout/', views.AlumnosLogoutView.as_view(), name='alumnos_logout'),

    path('home/', views.AlumnosHomeView.as_view(), name='alumnos_home'),
    path('credencial/', views.AlumnosCredencialView.as_view(), name='alumnos_credencial'),

    path('crear/', views.AlumnosCrearView.as_view(), name='alumnos_crear'),
]