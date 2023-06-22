from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group

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

class  AlumnosCredencialView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('alumnos/login/view_login_alumno.html')

        alumno = Alumno.objects.get(email=request.user.email)
        permite_visualizar = alumno.estado_credencial()

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
            "permite_visualizar": permite_visualizar
        }

        print(context)

        return render(request, 'alumnos/credencial/view_credencial_administradores.html', context=context)


class AlumnosHomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('alumnos/login/view_login_alumno.html')

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
            imagen=imagen
        )
        alumno.set_password(password1)
        alumno.save()
        alumno.crearCredencial()

        grupo_alumnos = Group.objects.get(name='Alumnos')
        grupo_alumnos.user_set.add(alumno)

        return render(request, 'alumnos/crear/view_crear_alumno.html', context={'success': 'Alumno creado correctamente, iniciar sesion: '})
