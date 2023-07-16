from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from core.models import Administrador, Alumno, Maestro, Directivo, UsuarioPersonalizado, Cuatrimestre, GradoDeEstudio, \
    Credencial, Carrera
from django.core.paginator import Paginator
from password_reset_application.MailService import Reset



TEMPLATES = [
    'administradores/login/view_login_administradores.html',
    'administradores/crear/view_crear_administradores.html',
    'administradores/home/view_home_administradores.html',
    'administradores/perfil/view_perfil_administrador.html',
]


def parser(user: str, email):
    model = None
    match user:
        case "administrador":
            try:
                model: Administrador = Administrador.objects.get(email=email)
                return model
            except:
                return None
        case "alumno":
            try:
                model = Alumno.objects.get(email=email)
                return model
            except:
                return None
        case _:
            pass


class AdministradoresLoginView(View):

    def get(self, request: HttpRequest):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("administradores_home")
        else:
            return render(request, TEMPLATES[0])

    def post(self, request: HttpRequest):
        email = request.POST.get("email")
        password = request.POST.get("password")

        administrativo: Administrador = parser("administrador", email)

        if administrativo is not None:
            if administrativo.check_password(password):
                login(request, authenticate(request, email=email, password=password))
                return redirect("administradores_home")
            else:
                return render(request, TEMPLATES[0], context={"error": "Contraseña inválida"})
        else:
            return render(request, TEMPLATES[0], context={"error": "Administrativo inexistente"})


class AdministradoresLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('administradores_login')


class AdministradoresCredencialView(View):
    def get(self, request):
        print("DirectivosCredencialView")
        if not request.user.is_authenticated:
            return redirect('administradores_home')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        administrador = Administrador.objects.get(email=request.user.email)

        permite_visualizar = administrador.estado_credencial()

        print(permite_visualizar)
        if administrador.contacto_emergencia_existe() == False or administrador.ficha_medica_existe() == False:
            permite_visualizar = False
        else:

            context = {
                "imagen": administrador.imagen.url,
                "nombre": administrador.nombre,
                "apellidos": administrador.apellidos,
                "email": administrador.email,
                "numero_telefono": administrador.numero_telefono,
                "direccion": administrador.direccion,
                "fecha_nacimiento": administrador.fecha_nacimiento,
                "tipo_usuario": "Directivo",
                "departamento": administrador.departamento,
                "estado_credencial": administrador.estado_credencial(),
                "permite_visualizar": permite_visualizar,
                "tipo_sangre": administrador.ficha_medica.tipo_sangre,
                "telefono_contacto_emergencia": administrador.contacto_emergencia.numero_contacto_emergencia
            }

            print(context)

            return render(request, 'administradores/credencial/view_credencial_administradores.html', context=context)
        context = {
            "permite_visualizar": permite_visualizar
        }
        return render(request, 'administradores/credencial/view_credencial_administradores.html', context=context)


class AdministradoresHomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('administradores_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        administrador = Administrador.objects.get(email=request.user.email)
        context = {
            "imagen": administrador.imagen.url,
            "nombre": administrador.nombre,
            "apellidos": administrador.apellidos,
            "email": administrador.email,
            "numero_telefono": administrador.numero_telefono,
            "direccion": administrador.direccion,
            "fecha_nacimiento": administrador.fecha_nacimiento,
            "departamento": administrador.departamento,
            "estado_credencial": administrador.estado_credencial()

        }
        return render(request, 'administradores/home/view_home_administradores.html', context=context)


class AdministradoresCrearView(View):

    def get(self, request: HttpRequest):
        return render(request, TEMPLATES[1])

    def post(self, request: HttpRequest):
        data = {}

        for key, value in request.POST.items():
            data[key] = value

        parser: Administrador = Administrador.objects.filter(email=data["email"]).exists()
        print(parser)

        if parser is False:
            if data["email"].endswith("@uptapachula.edu.mx"):
                if data["password"] == data["password_repeat"]:
                    email = data["email"]
                    password = data["password"]
                    data["imagen"] = request.FILES.get("imagen")
                    data["tipo_usuario"] = 'administrador'

                    del data["password_repeat"]
                    del data["csrfmiddlewaretoken"]
                    del data["email"]
                    del data["password"]

                    administrador = Administrador.objects.create(email=email, password=make_password(password), **data)
                    administrador.crearCredencial()
                    administrador.is_administrador = True
                    administrador.is_staff = True
                    administrador.save()

                    return render(request, TEMPLATES[1], context={'success': 'Administrador creado correctamente, iniciar sesión: '})
                else:
                    return render(request, TEMPLATES[1], context={"error": "Las contraseñas no coinciden"})
            else:
                return render(request, TEMPLATES[1], context={"error": "El correo no es institucional"})
        else:
            return render(request, TEMPLATES[1], context={"error": "Éste correo ya existe"})


class AdministradoresEditarView(View):

    def get(self, request: HttpRequest):
        if request.user.is_authenticated:
            administrador: Administrador = parser("administrador", request.user.email)

            return render(request, TEMPLATES[3], context={"admin": administrador})
        else:
            return redirect("administradores_login")

    def post(self, request: HttpRequest):
        if request.user.is_authenticated:
            administrador: Administrador = parser("administrador", request.user.email)
            imagen = administrador.imagen
            try:

                for key, value in request.POST.items():
                    setattr(administrador, key, value)

                if request.FILES.get("imagen") is not None:
                    administrador.imagen = request.FILES.get("imagen")
                else:
                    administrador.imagen = imagen

                administrador.save()

                return render(request, TEMPLATES[3], context={"mensaje": "Guardado correctamente", "admin": administrador})
            except:
                return render(request, TEMPLATES[3], context={"error": "Hubo un error en tus datos", "admin": administrador})
        else:
            return redirect("administradores_login")


class AdministradoresFichaMedicaView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('administradores_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        administrador = Administrador.objects.get(email=request.user.email)

        if administrador.requiereLlenarFichaMedica() or administrador.requiereLlenarContactoEmergencia():
            context = {
                "mensaje": "Por favor, llene su ficha medica y de contacto de emergencia antes de continuar, de lo contrario no podra activar su credencial",
                "tipo_sangre": '',
                "alergias": '',
                "enfermedades": '',
                "nombre_contacto_emergencia": '',
                "numero_contacto_emergencia": ''
            }
        else:
            context = {
                "tipo_sangre": administrador.ficha_medica.tipo_sangre,
                "alergias": administrador.ficha_medica.alergias,
                "enfermedades": administrador.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": administrador.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": administrador.contacto_emergencia.numero_contacto_emergencia,
            }

        return render(request, 'administradores/ficha_medica/view_ficha_medica_administradores.html', context=context)

    def post(self, request):

        administrador = Administrador.objects.get(email=request.user.email)
        if administrador.requiereLlenarFichaMedica() or administrador.requiereLlenarContactoEmergencia():
            administrador.crearFichaMedica(tipo_sangre=request.POST.get('tipo_sangre'),
                                           alergias=request.POST.get('alergias'),
                                           enfermedades_cronicas=request.POST.get('enfermedades'))
            administrador.crearContactoEmergencia(
                nombre=request.POST.get('nombre_contacto_emergencia'),
                numero_telefono=request.POST.get('numero_contacto_emergencia'))
            administrador.save()
            context = {
                "tipo_sangre": administrador.ficha_medica.tipo_sangre,
                "alergias": administrador.ficha_medica.alergias,
                "enfermedades": administrador.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": administrador.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": administrador.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'administradores/ficha_medica/view_ficha_medica_administradores.html',
                          context=context)

        else:
            administrador.ficha_medica.tipo_sangre = request.POST.get('tipo_sangre')
            administrador.ficha_medica.alergias = request.POST.get('alergias')
            administrador.ficha_medica.enfermedades = request.POST.get('enfermedades')
            administrador.contacto_emergencia.nombre_contacto_emergencia = request.POST.get(
                'nombre_contacto_emergencia')
            administrador.contacto_emergencia.numero_contacto_emergencia = request.POST.get(
                'numero_contacto_emergencia')
            administrador.ficha_medica.save()
            administrador.contacto_emergencia.save()
            context = {
                "tipo_sangre": administrador.ficha_medica.tipo_sangre,
                "alergias": administrador.ficha_medica.alergias,
                "enfermedades": administrador.ficha_medica.enfermedades,
                "nombre_contacto_emergencia": administrador.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": administrador.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'administradores/ficha_medica/view_ficha_medica_administradores.html',
                          context=context)


class AdministradorSolicitudCredencialView(View):
    def get(self, request):

        if not request.user.is_authenticated:
            return redirect('administradores_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        administrador = Administrador.objects.get(email=request.user.email)
        estado_ultima_solicitud = administrador.obtener_ultima_solicitud()

        lista_solicitudes = administrador.lista_solicitudes()
        if lista_solicitudes is None:
            lista_solicitudes = False

        if estado_ultima_solicitud is None:
            if administrador.ficha_medica_existe() == False or administrador.contacto_emergencia_existe() == False:
                print("No se puede solicitar credencial")
                context = {
                    "mensaje": "No puedes solicitar una credencial hasta que llenes tu ficha médica y contacto de emergencia",
                    "no_solicitud_datos_no": True,
                    "solicitudes": lista_solicitudes
                }
                return render(request, 'administradores/solicitud/view_solicitud_administrador.html', context=context)
            context = {
                "mensaje": "Solicita tu credencial",
                "solicitud_credencial": True,
                "solicitudes": lista_solicitudes
            }

            return render(request, 'administradores/solicitud/view_solicitud_administrador.html', context=context)
        if administrador.estado_ultima_solicitud() == 'pendiente':
            context = {
                "mensaje": "Ya tienes una solicitud pendiente",
                "no_solicitud_pendiente": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'administradores/solicitud/view_solicitud_administrador.html', context=context)

        if administrador.estado_credencial() == 'activa':
            context = {
                "mensaje": "Ya tienes una credencial activa",
                "no_solicitud_credencial_activa": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'administradores/solicitud/view_solicitud_administrador.html', context=context)

        context = {
            "mensaje": "Solicita tu credencial",
            "solicitud_credencial": True,
            "solicitudes": lista_solicitudes
        }

        return render(request, 'administradores/solicitud/view_solicitud_administrador.html', context=context)

    def post(self, request):
        administrador = Administrador.objects.get(email=request.user.email)
        administrador.generar_solicitud()
        context = {
            "mensaje": "Solicitud enviada",
            "solicitud_enviada": True
        }

        return render(request, 'administradores/solicitud/view_solicitud_administrador.html', context=context)


class AceptarSolicitud(View):

    def get(self, request, pk):
        usuario = UsuarioPersonalizado.objects.get(id=pk)
        usuario.aprobar_solicitud()
        return redirect('administradores_alumnos')


class RechazarSolicitud(View):

    def get(self, request, pk):
        usuario = UsuarioPersonalizado.objects.get(id=pk)
        usuario.rechazar_solicitud()
        return redirect('administradores_alumnos')

# ---------------------------------------------------------------------------------------------

# Vistas de alumnos

class PanelAdministradorAlumnosSolicitudes(View):
    def get(self, request):
        alumnos_pendientes = Alumno.objects.filter(solicitudes__estado='pendiente').order_by(
            'solicitudes__fecha_solicitud')

        if alumnos_pendientes.__len__() == 0:
            context = {
                "no_solicitudes": "No hay solicitudes pendientes"
            }
        else:
            context = {
                "alumnos_solicitudes_pendientes": alumnos_pendientes
            }

        return render(request,
                      'administradores/PanelAdministracion/administracion_alumnos/solicitudes/panel_solicitudes_alumnos.html',
                      context=context)

class PanelAdministradorAlumnosDatos(View):
    template_name = 'administradores/PanelAdministracion/administracion_alumnos/datos/panel_datos_alumnos.html'

    def get(self, request):
        alumnos = Alumno.objects.all()

        context = {
            'alumnos': alumnos
        }

        return render(request, self.template_name, context=context)

    def post(self, request):
        try:
            alumno = Alumno.objects.get(matricula=request.POST['matricula'])
        except Alumno.DoesNotExist:
            return render(request, self.template_name, context={'error': 'No existe un alumno con esa matrícula'})

        # Obtener el parámetro de búsqueda (matrícula

        context = {
            'alumno': alumno
        }

        return render(request, self.template_name, context=context)


class PanelAdministradorAlumnoDetalle(View):
    def get(self, request, matricula):
        cuatrimestres = Cuatrimestre.objects.all()
        grados = GradoDeEstudio.objects.all()
        carreras = Carrera.objects.all()

        alumno = Alumno.objects.get(matricula=matricula)
        context = {
            'alumno': alumno,
            'cuatrimestres': cuatrimestres,
            'grados': grados,
            'carreras': carreras
        }
        return render(request,
                      'administradores/PanelAdministracion/administracion_alumnos/detalles/panel_detalles_alumnos.html',
                      context=context)

    def post(self, request, matricula):
        alumno = Alumno.objects.get(matricula=matricula)

        alumno.carrera = Carrera.objects.get(id=request.POST.get('carrera'))
        alumno.cuatrimestre = Cuatrimestre.objects.get(id=request.POST.get('cuatrimestre'))
        alumno.gradoDeEstudio = GradoDeEstudio.objects.get(id=request.POST.get('grado_de_estudio'))
        alumno.email = request.POST.get('email')
        alumno.nombre = request.POST.get('nombre')
        alumno.apellidos = request.POST.get('apellidos')
        alumno.matricula = request.POST.get('matricula')
        alumno.numero_telefono = request.POST.get('numero_telefono')
        alumno.direccion = request.POST.get('direccion')
        alumno.fecha_nacimiento = request.POST.get('fecha_nacimiento')

        alumno.save()

        mensaje = 'Los datos del alumno se han actualizado correctamente.'
        cuatrimestres = Cuatrimestre.objects.all()
        grados = GradoDeEstudio.objects.all()
        carreras = Carrera.objects.all()

        context = {
            'alumno': alumno,
            'cuatrimestres': cuatrimestres,
            'grados': grados,
            'carreras': carreras,
            'mensaje': mensaje
        }

        return render(request,
                      'administradores/PanelAdministracion/administracion_alumnos/detalles/panel_detalles_alumnos.html',
                      context=context)


# Fin de vistas de alumnos

# ---------------------------------------------------------------------------------------------

# Views para activar y desactivar credenciales
class PanelAdministradoresDesactivarCredencial(View):

    def get(self, request, id):
        print("el id es:", id)
        credencial = Credencial.objects.get(id=id)
        credencial.desactivar()

        tipo_usuario = UsuarioPersonalizado.objects.get(id=credencial.usuario_id).tipo_usuario

        if tipo_usuario == 'alumno':
            return redirect('administradores_alumnos_lista')
        elif tipo_usuario == 'maestro':
            return redirect('administradores_maestros_lista')
        elif tipo_usuario == 'administrador':
            return redirect('administradores_administradores_lista')
        else:
            return redirect('administradores_directivos_lista')


class PanelAministradoresActivarCredencial(View):

    def get(self, request, id):
        credencial = Credencial.objects.get(id=id)
        credencial.activar()
        print(id)

        tipo_usuario = UsuarioPersonalizado.objects.get(id=credencial.usuario_id).tipo_usuario

        if tipo_usuario == 'alumno':
            return redirect('administradores_alumnos_lista')
        elif tipo_usuario == 'maestro':
            return redirect('administradores_maestros_lista')
        elif tipo_usuario == 'administrador':
            return redirect('administradores_administradores_lista')
        else:
            return redirect('administradores_directivos_lista')


# fin de views para activar y desactivar credenciales

# ---------------------------------------------------------------------------------------------


# Vistas de maestros


class PanelAdministradorMaestrosSolicitudes(View):
    def get(self, request):
        maestros_pendientes = Maestro.objects.filter(solicitudes__estado='pendiente').order_by(
            'solicitudes__fecha_solicitud')

        print(maestros_pendientes)
        if maestros_pendientes.count() == 0:
            context = {
                "no_solicitudes": "No hay solicitudes pendientes"
            }
        else:
            context = {
                "maestros_solicitudes_pendientes": maestros_pendientes
            }

        return render(request,
                      'administradores/PanelAdministracion/administracion_maestros/solicitudes/panel_solicitudes_maestros.html',
                      context=context)


class PanelAdministradorMaestrosDatos(View):
    def get(self, request):
        maestros = Maestro.objects.all()

        context = {
            'usuarios': maestros
        }

        return render(request,
                      'administradores/PanelAdministracion/administracion_maestros/datos/panel_datos_maestro.html',
                      context=context)

    def post(self, request):
        try:
            maestro = Maestro.objects.get(email=request.POST['email'])
            print(maestro)
        except Maestro.DoesNotExist:
            return render(request,
                          'administradores/PanelAdministracion/administracion_maestros/datos/panel_datos_maestro.html',
                          context={'error': 'No existe un maestro con ese correo'})

        context = {
            'usuario': maestro
        }

        return render(request,
                      'administradores/PanelAdministracion/administracion_maestros/datos/panel_datos_maestro.html',
                      context=context)


class PanelAdministradorMaestroDetalle(View):
    def get(self, request, id):
        maestro = Maestro.objects.get(id=id)
        context = {
            'usuario': maestro
        }
        return render(request,
                      'administradores/PanelAdministracion/administracion_maestros/detalles/panel_detalles_maestros.html',
                      context=context)

    def post(self, request, id):
        maestro = Maestro.objects.get(id=id)

        maestro.nombre = request.POST.get('nombre')
        maestro.apellidos = request.POST.get('apellidos')
        maestro.email = request.POST.get('email')
        maestro.numero_telefono = request.POST.get('numero_telefono')
        maestro.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        maestro.especialidad = request.POST.get('especialidad')

        maestro.save()

        mensaje = 'Los datos del maestro se han actualizado correctamente.'

        context = {
            'usuario': maestro,
            'mensaje': mensaje
        }

        return render(request,
                      'administradores/PanelAdministracion/administracion_maestros/detalles/panel_detalles_maestros.html',
                      context=context)


# Fin de vistas de maestros

# ---------------------------------------------------------------------------------------------

# Vistas de Administradores

class PanelAdministradorAdministradorSolicitudes(View):
    def get(self, request):
        administradores_pendientes = Administrador.objects.filter(solicitudes__estado='pendiente').order_by(
            'solicitudes__fecha_solicitud')

        if administradores_pendientes.count() == 0:
            context = {
                "no_solicitudes": "No hay solicitudes pendientes"
            }
        else:
            context = {
                "maestros_solicitudes_pendientes": administradores_pendientes
            }

        return render(request,
                      'administradores/PanelAdministracion/administracion_administradores/solicitudes/panel_solicitudes_administrador.html',
                      context=context)


class PanelAdministradorAdministradorsDatos(View):
    def get(self, request):
        administradores = Administrador.objects.all()

        context = {
            'usuarios': administradores
        }

        return render(request, 'administradores/PanelAdministracion/administracion_administradores/datos/panel_datos_administrador.html', context=context)

    def post(self, request):
        try:
            administrador = Administrador.objects.get(email=request.POST['email'])
        except Administrador.DoesNotExist:
            return render(request,
                          'administradores/PanelAdministracion/administracion_administradores/datos/panel_datos_administrador.html',
                          context={'error': 'No existe un administrador con ese correo'})

        context = {
            'usuario': administrador
        }

        return render(request,
                      'administradores/PanelAdministracion/administracion_administradores/datos/panel_datos_administrador.html',
                      context=context)


class PanelAdministradorAdministradorDetalle(View):
    def get(self, request, id):
        administrador = Administrador.objects.get(id=id)
        context = {
            'usuario': administrador
        }
        return render(request,
                      'administradores/PanelAdministracion/administracion_administradores/detalles/panel_detalles_administrador.html',
                      context=context)

    def post(self, request, id):
        administrador = Administrador.objects.get(id=id)

        administrador.nombre = request.POST.get('nombre')
        administrador.apellidos = request.POST.get('apellidos')
        administrador.email = request.POST.get('email')
        administrador.numero_telefono = request.POST.get('numero_telefono')
        administrador.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        administrador.departamento = request.POST.get('departamento')

        administrador.save()

        mensaje = 'Los datos del administrador se han actualizado correctamente.'

        context = {
            'usuario': administrador,
            'mensaje': mensaje
        }

        return render(request,
                      'administradores/PanelAdministracion/administracion_administradores/detalles/panel_detalles_administrador.html',
                      context=context)


# CORREO RECUERDA CONTRASEÑA
class AdministradorRestaurarPassword(View):

    def get(self, request):
        return render(request, 'administradores/restaurar_password/restore.html')

    def post(self, request):
        email = request.POST.get('email_required')
        fecha_nacimiento = request.POST.get('date_required')
        service = Reset()

        try:
            administrador = Administrador.objects.get(email=email)

            if email.endswith('@uptapachula.edu.mx') and str(administrador.fecha_nacimiento) == fecha_nacimiento:
                administrador.password = make_password(service.send(email, f"{administrador.nombre} {administrador.apellidos}"))
                administrador.save()
                return redirect("administrador_aceptado")
            else:
                return redirect('administrador_error')
        except Exception as e:
            return redirect('administrador_error')


class ErrorView(View):
    def get(self, request):
        return render(request, 'administradores/restaurar_password/errors.html')


class AceptacionCambio(View):
    def get(self, request):
        return render(request, 'administradores/restaurar_password/accepted.html')