from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.AdministradoresLoginView.as_view(), name='administradores_login'),
    path('logout/', views.AdministradoresLogoutView.as_view(), name='administradores_logout'),

    path('home/', views.AdministradoresHomeView.as_view(), name='administradores_home'),
    path('credencial/', views.AdministradoresCredencialView.as_view(), name='administradores_credencial'),
    path('perfil/', views.AdministradoresEditarView.as_view(), name='administradores_editar'),

    path('ficha_medica_contacto_emergencia/', views.AdministradoresFichaMedicaView.as_view(),
         name='administradores_ficha_medica_contacto_emergencia'),
    path('solicitudes/', views.AdministradorSolicitudCredencialView.as_view(), name='administradores_solicitudes'),

    path('crear/', views.AdministradoresCrearView.as_view(), name='administradores_crear'),

    path('panel_administrador/alumnos/', views.PanelAdministradorAlumnosSolicitudes.as_view(),
         name='administradores_alumnos'),
    path('panel_administrador/alumnos/lista/', views.PanelAdministradorAlumnosDatos.as_view(),
         name='administradores_alumnos_lista'),
    path('panel_administrador/alumnos/<str:matricula>', views.PanelAdministradorAlumnosDatos.as_view(),
         name='administradores_alumnos_datos'),
    path('panel_administrador/alumnos/detalle/<str:matricula>/editar/', views.PanelAdministradorAlumnoDetalle.as_view(),
         name='administradores_alumnos_editar'),
    path('panel_administrador/desactivar_credencial/<int:id>', views.PanelAdministradoresDesactivarCredencial.as_view(),
         name='administradores_desactivar_credencial'),
    path('panel_administrador/activar_credencial/<int:id>', views.PanelAministradoresActivarCredencial.as_view(),
         name='administradores_activar_credencial'),

    path('panel_administrador/directivos/', views.PanelAdministradorDirectivosSolicitudes.as_view(),
         name='administradores_directivos'),
    path('panel_administrador/directivos/lista/', views.PanelAdministradorDirectivosDatos.as_view(),
         name='administradores_directivos_lista'),
    path('panel_administrador/directivos/detalle/<int:id>', views.PanelAdministradorDirectivoDetalle.as_view(),
         name='administradores_directivos_detalle'),

    path('panel_administrador/maestros/', views.PanelAdministradorMaestrosSolicitudes.as_view(),
         name='administradores_maestros'),
    path('panel_administrador/maestros/lista/', views.PanelAdministradorMaestrosDatos.as_view(),
         name='administradores_maestros_lista'),
    path('panel_administrador/maestros/detalle/<int:id>/', views.PanelAdministradorMaestroDetalle.as_view(),
         name='administradores_maestros_detalle'),

    path('panel_administrador/administradores/', views.PanelAdministradorAdministradorSolicitudes.as_view(),
         name='administradores_administradores'),
    path('panel_administrador/administradores/lista/', views.PanelAdministradorAdministradorsDatos.as_view(),
         name='administradores_administradores_lista'),
    path('panel_administrador/administradores/detalle/<int:id>/',
         views.PanelAdministradorAdministradorDetalle.as_view(),
         name='administradores_administradores_detalle'),

    path('recuperar/', views.AdministradorRestaurarPassword.as_view(), name='administrador_recuperar'),
    path('error/', views.ErrorView.as_view(), name='administrador_error'),
    path('aceptado/', views.AceptacionCambio.as_view(), name='administrador_aceptado'),

    path('aceptar/<int:pk>/', views.AceptarSolicitud.as_view(), name='administradores_aceptar_credencial'),
    path('rechazar/<int:pk>/', views.RechazarSolicitud.as_view(), name='administradores_rechazar_credencial'),

]
