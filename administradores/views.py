from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login, logout

from core.models import Administrador


class AdministradoresLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('administradores_home')
        return render(request, 'administradores/login/view_login_administradores.html')

    def post(self, request):

        email = request.POST.get('email')
        password = request.POST.get('password')

        login_user = authenticate(request, email=email, password=password)
        if login_user is not None:
            login(request, login_user)

            try:
                administrador = Administrador.objects.get(email=email)
                return redirect('administradores_home')
            except Administrador.DoesNotExist:
                logout(request)
                return render(request, 'administradores/login/view_login_administradores.html',
                              {'error': 'No existe un administrador con ese correo'})
        return render(request, 'administradores/login/view_login_administradores.html',
                      {'error': 'Correo o contraseña incorrectos'})


class AdministradoresLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('administradores_login')


class AdministradoresCredencialView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('administradores_login')


        tipo_usuario = request.user.tipo_usuario
        if tipo_usuario == 'alumno':
            print('alumno')
            return redirect('alumnos_home')
        elif tipo_usuario == 'directivo':
            return redirect('directivos_home')
        elif tipo_usuario == 'maestro':
            return redirect('maestros_home')

        administrador = Administrador.objects.get(email=request.user.email)

        permite_visualizar = administrador.estado_credencial()
        context = {
            "imagen": administrador.imagen.url,
            "nombre": administrador.nombre,
            "apellidos": administrador.apellidos,
            "email": administrador.email,
            "numero_telefono": administrador.numero_telefono,
            "direccion": administrador.direccion,
            "fecha_nacimiento": administrador.fecha_nacimiento,
            "departamento": administrador.departamento,
            "estado_credencial": administrador.estado_credencial(),
            "permite_visualizar": permite_visualizar,

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

    # campos:
    # email, nombre, apellidos, fecha_nacimiento, direccion, numero_telefono, departamento, imagen

    def get(self, request):
        return render(request, 'administradores/crear/view_crear_administradores.html')

    def post(self, request):
        nombre = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        departamento = request.POST.get('departamento')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        imagen = request.FILES.get('imagen')

        if password1 != password2:
            return render(request, 'administradores/crear/view_crear_administradores.html',
                          {'error': 'Las contraseñas no coinciden'})
        if Administrador.objects.filter(email=email).exists():
            return render(request, 'administradores/crear/view_crear_administradores.html',
                          {'error': 'Este correo ya esta registrado'})

        administrador = Administrador.objects.create(
            email=email,
            nombre=nombre,
            apellidos=apellidos,
            numero_telefono=numero_telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            departamento=departamento,
            imagen=imagen,
            tipo_usuario='administrador'
        )
        administrador.set_password(password1)
        administrador.save()
        administrador.crearCredencial()
        administrador.hacerAdmin()
        grupo_administrativos = Group.objects.get(name='Administrativos')
        administrador.groups.add(grupo_administrativos)

        return render(request, 'administradores/crear/view_crear_administradores.html',
                      context={'success': 'Administrador creado correctamente, iniciar sesion: '})


class AdministradoresEditarView(View):
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
            "nombre": administrador.nombre,
            "apellidos": administrador.apellidos,
            "email": administrador.email,
            "numero_telefono": administrador.numero_telefono,
            "direccion": administrador.direccion,
            "fecha_nacimiento": administrador.fecha_nacimiento,
            "departamento": administrador.departamento,
            "estado_credencial": administrador.estado_credencial(),
            "imagen": administrador.imagen.url,
        }

        return render(request, 'administradores/perfil/view_perfil_administrador.html', context=context)

    def post(self, request):
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        departamento = request.POST.get('departamento')
        imagen = request.FILES.get('imagen')
        admin_image = request.POST.get('admin_image')
        print(admin_image)

        administrador = Administrador.objects.get(email=request.user.email)
        administrador.nombre = nombre
        administrador.apellidos = apellidos
        administrador.email = email
        administrador.numero_telefono = numero_telefono
        administrador.direccion = direccion
        administrador.fecha_nacimiento = fecha_nacimiento
        administrador.departamento = departamento
        print(imagen)
        if imagen is not None:
            administrador.imagen = imagen
        administrador.save()

        context = {
            "nombre": administrador.nombre,
            "apellidos": administrador.apellidos,
            "email": administrador.email,
            "numero_telefono": administrador.numero_telefono,
            "direccion": administrador.direccion,
            "fecha_nacimiento": administrador.fecha_nacimiento,
            "departamento": administrador.departamento,
            "estado_credencial": administrador.estado_credencial(),
            "imagen": administrador.imagen.url,
            "mensaje": "Datos actualizados correctamente"
        }

        return render(request, 'administradores/perfil/view_perfil_administrador.html', context=context)


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
