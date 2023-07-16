from django.urls import path
from . import views

urlpatterns = [
    path('emergencia/<int:id_usuario>', views.qr.as_view(), name='qr'),
    path('cambiar_password/', views.CambiarPassword.as_view(), name='cambiar_password'),
    path('cambiar_password_admin/', views.CambiarPasswordAdmin.as_view(), name='cambiar_password_admin'),
]