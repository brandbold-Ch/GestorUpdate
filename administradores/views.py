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
            return redirect('administradores_home')

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
        )
        administrador.set_password(password1)
        administrador.save()
        administrador.crearCredencial()
        administrador.hacerAdmin()
        grupo_administrativos = Group.objects.get(name='Administrativos')
        administrador.groups.add(grupo_administrativos)

        return render(request, 'administradores/crear/view_crear_administradores.html',
                      context={'success': 'Administrador creado correctamente, iniciar sesion: '})
