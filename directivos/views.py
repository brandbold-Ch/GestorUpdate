from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login, logout

from core.models import Directivo
from password_reset_application.MailService import Reset


class DirectivosLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('directivos_home')
        return render(request, 'directivos/login/view_login_directivos.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        login_user = authenticate(request, email=email, password=password)
        if login_user is not None:
            login(request, login_user)
            return redirect('directivos_home')

        return render(request, 'directivos/login/view_login_directivos.html',
                      {'error': 'Correo o contraseña incorrectos'})


class DirectivosLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('directivos_login')


class DirectivosCredencialView(View):
    def get(self, request):
        print("DirectivosCredencialView")
        if not request.user.is_authenticated:
            return redirect('alumnos/login/view_login_alumno.html')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        directivo = Directivo.objects.get(email=request.user.email)

        permite_visualizar = directivo.estado_credencial()

        print(permite_visualizar)
        if directivo.contacto_emergencia_existe() == False or directivo.ficha_medica_existe() == False:
            permite_visualizar = False
        else:

            context = {
                "imagen": directivo.imagen.url,
                "nombre": directivo.nombre,
                "apellidos": directivo.apellidos,
                "email": directivo.email,
                "numero_telefono": directivo.numero_telefono,
                "direccion": directivo.direccion,
                "fecha_nacimiento": directivo.fecha_nacimiento,
                "tipo_usuario": "Directivo",
                "puesto": directivo.puesto,
                "estado_credencial": directivo.estado_credencial(),
                "permite_visualizar": permite_visualizar,
                "tipo_sangre": directivo.ficha_medica.tipo_sangre,
                "telefono_contacto_emergencia": directivo.contacto_emergencia.numero_contacto_emergencia
            }

            print(context)

            return render(request, 'directivos/credencial/view_credencial_directivos.html', context=context)
        context = {
            "permite_visualizar": permite_visualizar
        }
        return render(request, 'directivos/credencial/view_credencial_directivos.html', context=context)


class DirectivosHomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('directivos_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        directivo = Directivo.objects.get(email=request.user.email)

        context = {
            "imagen": directivo.imagen.url,
            "nombre": directivo.nombre,
            "apellidos": directivo.apellidos,
            "email": directivo.email,
            "numero_telefono": directivo.numero_telefono,
            "direccion": directivo.direccion,
            "fecha_nacimiento": directivo.fecha_nacimiento,
            "puesto": directivo.puesto,
            "estado_credencial": directivo.estado_credencial()
        }

        return render(request, 'directivos/home/view_home_directivos.html', context=context)


class DirectivosCrearView(View):

    def get(self, request):
        return render(request, 'directivos/crear/view_crear_directivos.html')

    def post(self, request):
        # campos
        # nombre, email, apellidos, fecha_nacimiento, direccion, numero_telefono, imagen, puesto
        nombre = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        puesto = request.POST.get('puesto')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        imagen = request.FILES.get('imagen')

        if password1 != password2:
            return render(request, 'directivos/crear/view_crear_directivos.html',
                          {'error': 'Las contraseñas no coinciden'})
        if Directivo.objects.filter(email=email).exists():
            return render(request, 'directivos/crear/view_crear_directivos.html',
                          {'error': 'Este correo ya esta registrado'})

        directivo = Directivo.objects.create(
            email=email,
            nombre=nombre,
            apellidos=apellidos,
            numero_telefono=numero_telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            puesto=puesto,
            imagen=imagen,
            tipo_usuario='directivo'
        )
        directivo.set_password(password1)
        directivo.save()
        directivo.crearCredencial()

        print('deberia de llegar aqui')

        return render(request, 'directivos/crear/view_crear_directivos.html',
                      context={'success': 'Directivo creado con exito, iniciar sesion: '})


class DirectivosPerfilView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('directivos_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        directivo = Directivo.objects.get(email=request.user.email)

        context = {
            "imagen": directivo.imagen.url,
            "nombre": directivo.nombre,
            "apellidos": directivo.apellidos,
            "email": directivo.email,
            "numero_telefono": directivo.numero_telefono,
            "direccion": directivo.direccion,
            "fecha_nacimiento": directivo.fecha_nacimiento,
            "puesto": directivo.puesto,
            "estado_credencial": directivo.estado_credencial()
        }

        return render(request, 'directivos/perfil/view_perfil_administrador.html', context=context)

    def post(self, request):
        # campos
        # nombre, email, apellidos, fecha_nacimiento, direccion, numero_telefono, imagen, puesto
        nombre = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        puesto = request.POST.get('puesto')
        imagen = request.FILES.get('imagen')

        directivo = Directivo.objects.get(email=request.user.email)

        directivo.nombre = nombre
        directivo.apellidos = apellidos
        directivo.email = email
        directivo.numero_telefono = numero_telefono
        directivo.direccion = direccion
        directivo.fecha_nacimiento = fecha_nacimiento
        directivo.puesto = puesto
        if imagen is not None:
            directivo.imagen = imagen

        directivo.save()

        context = {
            "imagen": directivo.imagen.url,
            "nombre": directivo.nombre,
            "apellidos": directivo.apellidos,
            "email": directivo.email,
            "numero_telefono": directivo.numero_telefono,
            "direccion": directivo.direccion,
            "fecha_nacimiento": directivo.fecha_nacimiento,
            "puesto": directivo.puesto,
            "estado_credencial": directivo.estado_credencial(),
            "mensaje": "Datos actualizados con exito"
        }

        return render(request, 'directivos/perfil/view_perfil_administrador.html', context=context)


class DirectivoFichaMedicaView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('administradores_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        directivo = Directivo.objects.get(email=request.user.email)

        if directivo.requiereLlenarFichaMedica() or directivo.requiereLlenarContactoEmergencia():
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
                "tipo_sangre": directivo.ficha_medica.tipo_sangre,
                "alergias": directivo.ficha_medica.alergias,
                "enfermedades": directivo.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": directivo.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": directivo.contacto_emergencia.numero_contacto_emergencia,
            }

        return render(request, 'directivos/ficha_medica/view_ficha_medica_directivo.html', context=context)

    def post(self, request):

        directivo = Directivo.objects.get(email=request.user.email)
        if directivo.requiereLlenarFichaMedica() or directivo.requiereLlenarContactoEmergencia():
            directivo.crearFichaMedica(tipo_sangre=request.POST.get('tipo_sangre'),
                                       alergias=request.POST.get('alergias'),
                                       enfermedades_cronicas=request.POST.get('enfermedades'))
            directivo.crearContactoEmergencia(
                nombre=request.POST.get('nombre_contacto_emergencia'),
                numero_telefono=request.POST.get('numero_contacto_emergencia'))
            directivo.save()
            context = {
                "tipo_sangre": directivo.ficha_medica.tipo_sangre,
                "alergias": directivo.ficha_medica.alergias,
                "enfermedades": directivo.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": directivo.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": directivo.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'directivos/ficha_medica/view_ficha_medica_directivo.html',
                          context=context)

        else:
            directivo.ficha_medica.tipo_sangre = request.POST.get('tipo_sangre')
            directivo.ficha_medica.alergias = request.POST.get('alergias')
            directivo.ficha_medica.enfermedades = request.POST.get('enfermedades')
            directivo.contacto_emergencia.nombre_contacto_emergencia = request.POST.get(
                'nombre_contacto_emergencia')
            directivo.contacto_emergencia.numero_contacto_emergencia = request.POST.get(
                'numero_contacto_emergencia')
            directivo.ficha_medica.save()
            directivo.contacto_emergencia.save()
            context = {
                "tipo_sangre": directivo.ficha_medica.tipo_sangre,
                "alergias": directivo.ficha_medica.alergias,
                "enfermedades": directivo.ficha_medica.enfermedades,
                "nombre_contacto_emergencia": directivo.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": directivo.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'directivos/ficha_medica/view_ficha_medica_directivo.html',
                          context=context)


class DirectivoSolicitudCredencialView(View):
    def get(self, request):

        if not request.user.is_authenticated:
            return redirect('administradores_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        directivo = Directivo.objects.get(email=request.user.email)
        estado_ultima_solicitud = directivo.obtener_ultima_solicitud()

        lista_solicitudes = directivo.lista_solicitudes()
        if lista_solicitudes is None:
            lista_solicitudes = False

        if estado_ultima_solicitud is None:
            if directivo.ficha_medica_existe() == False or directivo.contacto_emergencia_existe() == False:
                print("No se puede solicitar credencial")
                context = {
                    "mensaje": "No puedes solicitar una credencial hasta que llenes tu ficha médica y contacto de emergencia",
                    "no_solicitud_datos_no": True,
                    "solicitudes": lista_solicitudes
                }
                return render(request, 'directivos/solicitud/view_solicitud_directivo.html', context=context)
            context = {
                "mensaje": "Solicita tu credencial",
                "solicitud_credencial": True,
                "solicitudes": lista_solicitudes
            }

            return render(request, 'directivos/solicitud/view_solicitud_directivo.html', context=context)
        if directivo.estado_ultima_solicitud() == 'pendiente':
            context = {
                "mensaje": "Ya tienes una solicitud pendiente",
                "no_solicitud_pendiente": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'directivos/solicitud/view_solicitud_directivo.html', context=context)

        if directivo.estado_credencial() == 'activa':
            context = {
                "mensaje": "Ya tienes una credencial activa",
                "no_solicitud_credencial_activa": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'directivos/solicitud/view_solicitud_directivo.html', context=context)

        context = {
            "mensaje": "Solicita tu credencial",
            "solicitud_credencial": True,
            "solicitudes": lista_solicitudes
        }

        return render(request, 'directivos/solicitud/view_solicitud_directivo.html', context=context)

    def post(self, request):
        directivo = Directivo.objects.get(email=request.user.email)
        directivo.generar_solicitud()
        context = {
            "mensaje": "Solicitud enviada",
            "solicitud_enviada": True
        }

        return render(request, 'directivos/solicitud/view_solicitud_directivo.html', context=context)

# CORREO RECUPERACION DE CONTRASEÑA
class DirectivoRestaurarPassword(View):

    def get(self, request):
        return render(request, 'alumnos/restaurar_password/restore.html')

    def post(self, request):
        email = request.POST.get('email_required')
        fecha_nacimiento = request.POST.get('date_required')
        service = Reset()

        try:
            directivo = Directivo.objects.get(email=email)

            if email.endswith('@uptapachula.edu.mx') and str(directivo.fecha_nacimiento) == fecha_nacimiento:
                directivo.password = make_password(service.send(email, f"{directivo.nombre} {directivo.apellidos}"))
                directivo.save()
                return redirect("directivo_aceptado")
            else:
                return redirect('directivo_error')
        except Exception as e:
            return redirect('directivo_error')


class ErrorView(View):
    def get(self, request):
        return render(request, 'directivos/restaurar_password/errors.html')


class AceptacionCambio(View):
    def get(self, request):
        return render(request, 'directivos/restaurar_password/accepted.html')