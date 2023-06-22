from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.MaestrosLoginView.as_view(), name='maestros_login'),
    path('logout/', views.MaestrosLogoutView.as_view(), name='maestros_logout'),

    path('home/', views.MaestrosHomeView.as_view(), name='maestros_home'),
    path('credencial/', views.MaestrosCredencialView.as_view(), name='maestros_credencial'),

    path('crear/', views.MaestroCrearView.as_view(), name='maestros_crear'),
]
