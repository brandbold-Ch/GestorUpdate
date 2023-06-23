from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group

from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout

from core.models import Alumno, Carrera, Cuatrimestre, GradoDeEstudio


class AlumnosLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('alumnos_home')
        return render(request, 'alumnos/login/view_login_alumno.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        login_user = authenticate(request, email=email, password=password)
        if login_user is not None:
            login(request, login_user)
            return redirect('alumnos_home')

        return render(request, 'alumnos/login/view_login_alumno.html', {'error': 'Correo o contraseña incorrectos'})


class AlumnosCredencialView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('alumnos/login/view_login_alumno.html')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        alumno = Alumno.objects.get(email=request.user.email)

        permite_visualizar = alumno.estado_credencial()
        print(permite_visualizar)
        if alumno.contacto_emergencia_existe() == False or alumno.ficha_medica_existe() == False:
            permite_visualizar = False
        else:

            context = {
                "imagen": alumno.imagen.url,
                "nombre": alumno.nombre,
                "apellidos": alumno.apellidos,
                "email": alumno.email,
                "numero_telefono": alumno.numero_telefono,
                "direccion": alumno.direccion,
                "fecha_nacimiento": alumno.fecha_nacimiento,
                "matricula": alumno.matricula,
                "tipo_alumno": alumno.gradoDeEstudio.grado,
                "carrera": alumno.carrera.nombre_carrera,
                "cuatrimestre": alumno.cuatrimestre.numero_cuatrimestre,
                "estado_credencial": alumno.estado_credencial(),
                "permite_visualizar": permite_visualizar,
                "tipo_sangre": alumno.ficha_medica.tipo_sangre,
                "telefono_contacto_emergencia": alumno.contacto_emergencia.numero_contacto_emergencia
            }

            print(context)

            return render(request, 'alumnos/credencial/view_credencial_administradores.html', context=context)
        context = {
            "permite_visualizar": permite_visualizar
        }
        return render(request, 'alumnos/credencial/view_credencial_administradores.html', context=context)


class AlumnosHomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('alumnos/login/view_login_alumno.html')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        alumno = Alumno.objects.get(email=request.user.email)

        context = {
            "imagen": alumno.imagen.url,
            "nombre": alumno.nombre,
            "apellidos": alumno.apellidos,
            "email": alumno.email,
            "numero_telefono": alumno.numero_telefono,
            "direccion": alumno.direccion,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "matricula": alumno.matricula,
            "tipo_alumno": alumno.gradoDeEstudio.grado,
            "carrera": alumno.carrera.nombre_carrera,
            "cuatrimestre": alumno.cuatrimestre.numero_cuatrimestre,
            "estado_credencial": alumno.estado_credencial()
        }

        return render(request, 'alumnos/home/view_home_alumno.html', context=context)


class AlumnosLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('alumnos_login')


class AlumnosCrearView(View):
    def get(self, request):

        lista_carreras = Carrera.objects.all()
        lista_cuatrimestres = Cuatrimestre.objects.all()
        lista_grados = GradoDeEstudio.objects.all()

        context = {
            'lista_carreras': lista_carreras,
            'lista_cuatrimestres': lista_cuatrimestres,
            'lista_grados': lista_grados
        }

        return render(request, 'alumnos/crear/view_crear_alumno.html', context=context)

    def post(self, request):
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        matricula = request.POST.get('matricula')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        tipo_alumno = request.POST.get('tipo_alumno')
        cuatrimestre = request.POST.get('cuatrimestre')
        carrera = request.POST.get('carrera')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        imagen = request.FILES.get('imagen')

        carrera = Carrera.objects.get(id=carrera)
        cuatrimestre = Cuatrimestre.objects.get(id=cuatrimestre)
        grado_de_estudio = GradoDeEstudio.objects.get(id=tipo_alumno)

        if password1 != password2:
            return render(request, 'alumnos/crear/view_crear_alumno.html', {'error': 'Las contraseñas no coinciden'})
        if Alumno.objects.filter(email=email).exists():
            return render(request, 'alumnos/crear/view_crear_alumno.html', {'error': 'Este correo ya esta registrado'})
        if Alumno.objects.filter(matricula=matricula).exists():
            return render(request, 'alumnos/crear/view_crear_alumno.html',
                          {'error': 'Esta matricula ya esta registrada'})

        alumno = Alumno.objects.create(
            email=email,
            nombre=nombres,
            apellidos=apellidos,
            matricula=matricula,
            numero_telefono=numero_telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            gradoDeEstudio=grado_de_estudio,
            cuatrimestre=cuatrimestre,
            carrera=carrera,
            imagen=imagen,
            tipo_usuario='alumno'
        )
        alumno.set_password(password1)
        alumno.save()
        alumno.crearCredencial()

        return render(request, 'alumnos/crear/view_crear_alumno.html',
                      context={'success': 'Alumno creado correctamente, iniciar sesion: '})


class AlumnosFichaMedicaView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('alumnos_login')

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        alumno = Alumno.objects.get(email=request.user.email)

        if alumno.requiereLlenarFichaMedica() or alumno.requiereLlenarContactoEmergencia():
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
                "tipo_sangre": alumno.ficha_medica.tipo_sangre,
                "alergias": alumno.ficha_medica.alergias,
                "enfermedades": alumno.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": alumno.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": alumno.contacto_emergencia.numero_contacto_emergencia,
            }

        return render(request, 'alumnos/ficha_medica/view_ficha_medica_administradores.html', context=context)

    def post(self, request):

        alumno = Alumno.objects.get(email=request.user.email)
        if alumno.requiereLlenarFichaMedica() or alumno.requiereLlenarContactoEmergencia():
            alumno.crearFichaMedica(tipo_sangre=request.POST.get('tipo_sangre'),
                                    alergias=request.POST.get('alergias'),
                                    enfermedades_cronicas=request.POST.get('enfermedades'))
            alumno.crearContactoEmergencia(
                nombre=request.POST.get('nombre_contacto_emergencia'),
                numero_telefono=request.POST.get('numero_contacto_emergencia'))
            alumno.save()
            context = {
                "tipo_sangre": alumno.ficha_medica.tipo_sangre,
                "alergias": alumno.ficha_medica.alergias,
                "enfermedades": alumno.ficha_medica.enfermedades_cronicas,
                "nombre_contacto_emergencia": alumno.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": alumno.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'alumnos/ficha_medica/view_ficha_medica_administradores.html',
                          context=context)

        else:
            alumno.ficha_medica.tipo_sangre = request.POST.get('tipo_sangre')
            alumno.ficha_medica.alergias = request.POST.get('alergias')
            alumno.ficha_medica.enfermedades = request.POST.get('enfermedades')
            alumno.contacto_emergencia.nombre_contacto_emergencia = request.POST.get(
                'nombre_contacto_emergencia')
            alumno.contacto_emergencia.numero_contacto_emergencia = request.POST.get(
                'numero_contacto_emergencia')
            alumno.ficha_medica.save()
            alumno.contacto_emergencia.save()
            context = {
                "tipo_sangre": alumno.ficha_medica.tipo_sangre,
                "alergias": alumno.ficha_medica.alergias,
                "enfermedades": alumno.ficha_medica.enfermedades,
                "nombre_contacto_emergencia": alumno.contacto_emergencia.nombre_contacto_emergencia,
                "numero_contacto_emergencia": alumno.contacto_emergencia.numero_contacto_emergencia,
                "mensaje": "Datos actualizados correctamente"
            }

            return render(request, 'alumnos/ficha_medica/view_ficha_medica_administradores.html',
                          context=context)


class AlumnoPerfilView(View):
    def get(self, request):

        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'administrador':
            return redirect('administradores_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        alumno = Alumno.objects.get(email=request.user.email)

        context = {
            "email": alumno.email,
            "nombre": alumno.nombre,
            "apellidos": alumno.apellidos,
            "matricula": alumno.matricula,
            "numero_telefono": alumno.numero_telefono,
            "direccion": alumno.direccion,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "grado_de_estudio": alumno.gradoDeEstudio,
            "cuatrimestre": alumno.cuatrimestre,
            "carrera": alumno.carrera,
            "imagen": alumno.imagen.url,
        }

        return render(request, 'alumnos/perfil/view_perfil_administrador.html', context=context)

    def post(self, request):
        alumno = Alumno.objects.get(email=request.user.email)

        alumno.nombre = request.POST.get('nombre')
        alumno.apellidos = request.POST.get('apellidos')
        alumno.matricula = request.POST.get('matricula')
        alumno.numero_telefono = request.POST.get('numero_telefono')
        alumno.direccion = request.POST.get('direccion')
        alumno.fecha_nacimiento = request.POST.get('fecha_nacimiento')

        imagen = request.FILES.get('imagen')

        if imagen is not None:
            alumno.imagen = imagen

        alumno.save()

        context = {
            "email": alumno.email,
            "nombre": alumno.nombre,
            "apellidos": alumno.apellidos,
            "matricula": alumno.matricula,
            "numero_telefono": alumno.numero_telefono,
            "direccion": alumno.direccion,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "grado_de_estudio": alumno.gradoDeEstudio,
            "cuatrimestre": alumno.cuatrimestre,
            "carrera": alumno.carrera,
            "imagen": alumno.imagen.url,
            "mensaje": "Datos actualizados correctamente"
        }

        return render(request, 'alumnos/perfil/view_perfil_administrador.html', context=context)


class AlumnoSolicitudCredencialView(View):
    def get(self, request):
        alumno = Alumno.objects.get(email=request.user.email)
        estado_ultima_solicitud = alumno.obtener_ultima_solicitud()

        lista_solicitudes = alumno.lista_solicitudes()
        if lista_solicitudes is None:
            lista_solicitudes = False


        if estado_ultima_solicitud is None:
            if alumno.ficha_medica_existe() == False or alumno.contacto_emergencia_existe() == False:
                print("No se puede solicitar credencial")
                context = {
                    "mensaje": "No puedes solicitar una credencial hasta que llenes tu ficha médica y contacto de emergencia",
                    "no_solicitud_datos_no": True,
                    "solicitudes": lista_solicitudes
                }
                return render(request, 'alumnos/solicitud/view_solicitud_alumno.html', context=context)
            context = {
                "mensaje": "Solicita tu credencial",
                "solicitud_credencial": True,
                "solicitudes": lista_solicitudes
            }

            return render(request, 'alumnos/solicitud/view_solicitud_alumno.html', context=context)
        if alumno.estado_ultima_solicitud() == 'pendiente':
            context = {
                "mensaje": "Ya tienes una solicitud pendiente",
                "no_solicitud_pendiente": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'alumnos/solicitud/view_solicitud_alumno.html', context=context)

        if alumno.estado_credencial() == 'activa':
            context = {
                "mensaje": "Ya tienes una credencial activa",
                "no_solicitud_credencial_activa": True,
                "solicitudes": lista_solicitudes
            }
            return render(request, 'alumnos/solicitud/view_solicitud_alumno.html', context=context)

        context = {
            "mensaje": "Solicita tu credencial",
            "solicitud_credencial": True,
            "solicitudes": lista_solicitudes
        }

        return render(request, 'alumnos/solicitud/view_solicitud_alumno.html', context=context)

    def post(self, request):
        alumno = Alumno.objects.get(email=request.user.email)
        alumno.generar_solicitud()
        context = {
            "mensaje": "Solicitud enviada",
            "solicitud_enviada": True
        }

        return render(request, 'alumnos/solicitud/view_solicitud_alumno.html', context=context)
