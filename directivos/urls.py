from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.DirectivosLoginView.as_view(), name='directivos_login'),
    path('logout/', views.DirectivosLogoutView.as_view(), name='directivos_logout'),

    path('home/', views.DirectivosHomeView.as_view(), name='directivos_home'),

    path('crear/', views.DirectivosCrearView.as_view(), name='directivos_crear'),
]