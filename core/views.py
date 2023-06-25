from django.shortcuts import render, redirect
from django.views import View

from .models import UsuarioPersonalizado




def error_404(request, exception):
    return render(request, 'core/404.html', status=404)


class qr(View):
    def get(self, request, id_usuario):

        usuario = UsuarioPersonalizado.objects.get(id=id_usuario)

        # datos de ficha medica y contacto de emergencia
        context = {
            'nombre': usuario.nombre,
            'apellidos': usuario.apellidos,
            'tipo_sangre': usuario.ficha_medica.tipo_sangre,
            'alergias': usuario.ficha_medica.alergias,
            'enfermedades': usuario.ficha_medica.enfermedades_cronicas,
            'nombre_contacto_emergencia': usuario.contacto_emergencia.nombre_contacto_emergencia,
            'telefono_contacto_emergencia': usuario.contacto_emergencia.numero_contacto_emergencia,
        }

        return render(request, 'core/qr_info.html', context=context)


class CambiarPassword(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect('home')

        if not request.user.is_authenticated:
            return render(request, 'core/cambiar_password.html', context={'no_autenticado': 'No estas autenticado'})
        usuario = UsuarioPersonalizado.objects.get(id=request.user.id)

        print(usuario)

        context = {
            "nombre_completo": f'{usuario.nombre} {usuario.apellidos}'
        }

        return render(request, 'core/cambiar_password.html', context=context)

    def post(self, request):
        print('POST')
        usuario = UsuarioPersonalizado.objects.get(id=request.user.id)
        nombre_completo = f'{usuario.nombre} {usuario.apellidos}'

        if request.POST['password1'] == request.POST['password2']:
            usuario.set_password(request.POST['password1'])
            usuario.save()
            return render(request, 'core/cambiar_password.html', context={'mensaje': 'Contraseña cambiada correctamente'})
        else:
            return render(request, 'core/cambiar_password.html', context={'mensaje': 'Las contraseñas no coinciden', 'nombre_completo': nombre_completo})


class CambiarPasswordAdmin(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect('home')

        if not request.user.is_authenticated:
            return render(request, 'core/cambiar_password.html', context={'no_autenticado': 'No estas autenticado'})
        usuario = UsuarioPersonalizado.objects.get(id=request.user.id)

        print(usuario)

        context = {
            "nombre_completo": f'{usuario.nombre} {usuario.apellidos}'
        }

        return render(request, 'core/cambiar_password.html', context=context)

    def post(self, request):
        print('POST')
        usuario = UsuarioPersonalizado.objects.get(id=request.user.id)
        nombre_completo = f'{usuario.nombre} {usuario.apellidos}'

        if request.POST['password1'] == request.POST['password2']:
            usuario.set_password(request.POST['password1'])
            usuario.save()
            return render(request, 'core/cambiar_password.html', context={'mensaje': 'Contraseña cambiada correctamente'})
        else:
            return render(request, 'core/cambiar_password.html', context={'mensaje': 'Las contraseñas no coinciden', 'nombre_completo': nombre_completo})

