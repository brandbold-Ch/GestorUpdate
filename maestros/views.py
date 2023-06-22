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
        if not request.user.is_authenticated:
            return redirect('maestros_login')

        maestro = Maestro.objects.get(email=request.user.email)
        permite_visualizar = maestro.estado_credencial()
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
            "permite_visualizar": permite_visualizar,

        }

        return render(request, 'maestros/credencial/view_credencial_administradores.html', context=context)

class MaestrosHomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('maestros_login')

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
        )
        maestro.set_password(password1)
        maestro.save()
        maestro.crearCredencial()

        grupo_docentes = Group.objects.get(name='Docentes')
        maestro.groups.add(grupo_docentes)

        return render(request, 'maestros/crear/view_crear_maestro.html', {'success': 'Maestro creado con exito, iniciar sesion: '})
