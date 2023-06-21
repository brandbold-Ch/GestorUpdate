from django.contrib import admin
from .models import Carrera, GradoDeEstudio, Cuatrimestre, Alumno, Administrador, Credencial, Directivo


admin.site.register(Carrera)
admin.site.register(GradoDeEstudio)
admin.site.register(Cuatrimestre)
admin.site.register(Alumno)
admin.site.register(Administrador)
admin.site.register(Credencial)
admin.site.register(Directivo)