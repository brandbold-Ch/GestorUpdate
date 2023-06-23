from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login, logout

from core.models import Maestro

class MaestrosLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('maestros_home')
        return render(request, 'maestros/login/view_login_maestro.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        login_user = authenticate(request, email=email, password=password)
        if login_user is not None:
            login(request, login_user)
            return redirect('maestros_home')

        return render(request, 'maestros/login/view_login_maestro.html', {'error': 'Correo o contraseña incorrectos'})

class MaestrosLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('maestros_login')

class MaestrosCredencialView(View):
    def get(self, request):
        print("DirectivosCredencialView")
        if not request.user.is_authenticated:
            return redirect('alumnos/login/view_login_alumno.html')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')

        maestro = Maestro.objects.get(email=request.user.email)

        permite_visualizar = maestro.estado_credencial()

        print(permite_visualizar)
        if maestro.contacto_emergencia_existe() == False or maestro.ficha_medica_existe() == False:
            permite_visualizar = False
        else:

            context = {
                "imagen": maestro.imagen.url,
                "nombre": maestro.nombre,
                "apellidos": maestro.apellidos,
                "email": maestro.email,
                "numero_telefono": maestro.numero_telefono,
                "direccion": maestro.direccion,
                "fecha_nacimiento": maestro.fecha_nacimiento,
                "tipo_usuario": "maestro",
                "especialidad": maestro.especialidad,
                "estado_credencial": maestro.estado_credencial(),
                "permite_visualizar": permite_visualizar,
                "tipo_sangre": maestro.ficha_medica.tipo_sangre,
                "telefono_contacto_emergencia": maestro.contacto_emergencia.numero_contacto_emergencia
            }

            print(context)

            return render(request, 'maestros/credencial/view_credencial_administradores.html', context=context)
        context = {
            "permite_visualizar": permite_visualizar
        }
        return render(request, 'maestros/credencial/view_credencial_administradores.html', context=context)

class MaestrosHomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('maestros_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')

        maestro = Maestro.objects.get(email=request.user.email)
        context = {
            "imagen": maestro.imagen.url,
            "nombre": maestro.nombre,
            "apellidos": maestro.apellidos,
            "email": maestro.email,
            "numero_telefono": maestro.numero_telefono,
            "direccion": maestro.direccion,
            "fecha_nacimiento": maestro.fecha_nacimiento,
            "especialidad": maestro.especialidad,
            "estado_credencial": maestro.estado_credencial(),
        }


        return render(request, 'maestros/home/view_home_maestro.html', context=context)

class MaestroCrearView(View):
    # campos
    # nombre, apellidos, email, fecha_nacimiento, direccion, numero_telefono, imagen, especialidad
    def get(self, request):
        return render(request, 'maestros/crear/view_crear_maestro.html')

    def post(self, request):
        nombre = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        especialidad = request.POST.get('especialidad')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        imagen = request.FILES.get('imagen')

        if password1 != password2:
            return render(request, 'maestros/crear/view_crear_maestro.html', {'error': 'Las contraseñas no coinciden'})
        if Maestro.objects.filter(email=email).exists():
            return render(request, 'maestros/crear/view_crear_maestro.html', {'error': 'Este correo ya esta registrado'})

        maestro = Maestro.objects.create(
            email=email,
            nombre=nombre,
            apellidos=apellidos,
            numero_telefono=numero_telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            especialidad=especialidad,
            imagen=imagen,
            tipo_usuario='maestro'
        )
        maestro.set_password(password1)
        maestro.save()
        maestro.crearCredencial()
        maestro.save()
        return render(request, 'maestros/crear/view_crear_maestro.html', {'success': 'Maestro creado con exito, iniciar sesion: '})

class MaestrosPerfilView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('directivos_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')

        maestro = Maestro.objects.get(email=request.user.email)

        context = {
            "imagen": maestro.imagen.url,
            "nombre": maestro.nombre,
            "apellidos": maestro.apellidos,
            "email": maestro.email,
            "numero_telefono": maestro.numero_telefono,
            "direccion": maestro.direccion,
            "fecha_nacimiento": maestro.fecha_nacimiento,
            "especialidad": maestro.especialidad,
            "estado_credencial": maestro.estado_credencial()
        }

        return render(request, 'maestros/perfil/view_perfil_maestro.html', context=context)

    def post(self, request):
        # campos
        # nombre, email, apellidos, fecha_nacimiento, direccion, numero_telefono, imagen, puesto
        nombre = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        especialidad = request.POST.get('especialidad')
        imagen = request.FILES.get('imagen')

        maestro = Maestro.objects.get(email=request.user.email)

        maestro.nombre = nombre
        maestro.apellidos = apellidos
        maestro.email = email
        maestro.numero_telefono = numero_telefono
        maestro.direccion = direccion
        maestro.fecha_nacimiento = fecha_nacimiento
        maestro.especialidad = especialidad
        if imagen is not None:
            maestro.imagen = imagen

        maestro.save()

        context = {
            "imagen": maestro.imagen.url,
            "nombre": maestro.nombre,
            "apellidos": maestro.apellidos,
            "email": maestro.email,
            "numero_telefono": maestro.numero_telefono,
            "direccion": maestro.direccion,
            "fecha_nacimiento": maestro.fecha_nacimiento,
            "especialidad": maestro.especialidad,
            "estado_credencial": maestro.estado_credencial(),
            "mensaje": "Datos actualizados con exito"
        }

        return render(request, 'maestros/perfil/view_perfil_maestro.html', context=context)


class MaestrosFichaMedicaView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('administradores_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'alumno':
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')

        maestro = Maestro.objects.get(email=request.user.email)

        if maestro.requiereLlenarFichaMedica() or maestro.requiereLlenarContactoEmergencia():
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
                "tipo_sangre": maestro.ficha_medica.tipo_sangre,
                "alergias": maestro.ficha_medica.alergias,
                "enfermedades": maestro.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": maestro.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": maestro.contacto_emergencia.numero_contacto_emergencia,
            }

        return render(request, 'maestros/ficha_medica/view_ficha_medica_maestro.html', context=context)

    def post(self, request):

        maestro = Maestro.objects.get(email=request.user.email)
        if maestro.requiereLlenarFichaMedica() or maestro.requiereLlenarContactoEmergencia():
            maestro.crearFichaMedica(tipo_sangre=request.POST.get('tipo_sangre'),
                                           alergias=request.POST.get('alergias'),
                                           enfermedades_cronicas=request.POST.get('enfermedades'))
            maestro.crearContactoEmergencia(
                nombre=request.POST.get('nombre_contacto_emergencia'),
                numero_telefono=request.POST.get('numero_contacto_emergencia'))
            maestro.save()
            context = {
                "tipo_sangre": maestro.ficha_medica.tipo_sangre,
                "alergias": maestro.ficha_medica.alergias,
                "enfermedades": maestro.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": maestro.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": maestro.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'maestros/ficha_medica/view_ficha_medica_maestro.html',
                          context=context)

        else:
            maestro.ficha_medica.tipo_sangre = request.POST.get('tipo_sangre')
            maestro.ficha_medica.alergias = request.POST.get('alergias')
            maestro.ficha_medica.enfermedades = request.POST.get('enfermedades')
            maestro.contacto_emergencia.nombre_contacto_emergencia = request.POST.get(
                'nombre_contacto_emergencia')
            maestro.contacto_emergencia.numero_contacto_emergencia = request.POST.get(
                'numero_contacto_emergencia')
            maestro.ficha_medica.save()
            maestro.contacto_emergencia.save()
            context = {
                "tipo_sangre": maestro.ficha_medica.tipo_sangre,
                "alergias": maestro.ficha_medica.alergias,
                "enfermedades": maestro.ficha_medica.enfermedades,
                "nombre_contacto_emergencia": maestro.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": maestro.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'maestros/ficha_medica/view_ficha_medica_maestro.html',
                          context=context)

class MaestroSolicitudCredencialView(View):
    def get(self, request):
        maestro = Maestro.objects.get(email=request.user.email)
        estado_ultima_solicitud = maestro.obtener_ultima_solicitud()

        lista_solicitudes = maestro.lista_solicitudes()
        if lista_solicitudes is None:
            lista_solicitudes = False

        if estado_ultima_solicitud is None:
            if maestro.ficha_medica_existe() == False or maestro.contacto_emergencia_existe() == False:
                print("No se puede solicitar credencial")
                context = {
                    "mensaje": "No puedes solicitar una credencial hasta que llenes tu ficha médica y contacto de emergencia",
                    "no_solicitud_datos_no": True,
                    "solicitudes": lista_solicitudes
                }
                return render(request, 'maestros/solicitud/view_solicitud_maestro.html', context=context)
            context = {
                "mensaje": "Solicita tu credencial",
                "solicitud_credencial": True,
                "solicitudes": lista_solicitudes
            }

            return render(request, 'maestros/solicitud/view_solicitud_maestro.html', context=context)
        if maestro.estado_ultima_solicitud() == 'pendiente':
            context = {
                "mensaje": "Ya tienes una solicitud pendiente",
                "no_solicitud_pendiente": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'maestros/solicitud/view_solicitud_maestro.html', context=context)

        if maestro.estado_credencial() == 'activa':
            context = {
                "mensaje": "Ya tienes una credencial activa",
                "no_solicitud_credencial_activa": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'maestros/solicitud/view_solicitud_maestro.html', context=context)

        context = {
            "mensaje": "Solicita tu credencial",
            "solicitud_credencial": True,
            "solicitudes": lista_solicitudes
        }

        return render(request, 'maestros/solicitud/view_solicitud_maestro.html', context=context)

    def post(self, request):
        maestro = Maestro.objects.get(email=request.user.email)
        maestro.generar_solicitud()
        context = {
            "mensaje": "Solicitud enviada",
            "solicitud_enviada": True
        }

        return render(request, 'maestros/solicitud/view_solicitud_maestro.html', context=context)