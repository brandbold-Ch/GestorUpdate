# Definicion de modelos base para usuarios
from django.core.exceptions import ValidationError
from django.db import models

from cloudinary.models import CloudinaryField

import uuid

# Importacion de clases para creacion de usuario personalizado
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
    AbstractUser
)

ESTADOS_SOLICITUD = (
    ('solicitada', 'solicitada'),
    ('aprobada', 'aprobada'),
    ('rechazada', 'rechazada')
)

TIPO_SOLICITUD = (
    ('primera', 'primera'),
    ('renovacion', 'renovacion')
)


# Modelos extra para los alumnos
class Cuatrimestre(models.Model):
    numero_cuatrimestre = models.IntegerField(unique=True, error_messages={'unique': 'Ya existe'})

    def __str__(self):
        return str(self.numero_cuatrimestre)


class Carrera(models.Model):
    nombre_carrera = models.CharField(max_length=50, unique=True, error_messages={'unique': 'Ya existe la carrera'})

    def __str__(self):
        return self.nombre_carrera


class GradoDeEstudio(models.Model):
    grado = models.CharField(max_length=20, unique=True, error_messages={'unique': 'Grado ya existente'})

    def __str__(self):
        return self.grado


# Modelos definidos para los usuarios en general

class ContactoEmergencia(models.Model):
    nombre_contacto_emergencia = models.CharField(max_length=60)
    numero_contacto_emergencia = models.CharField(max_length=10)
    usuario = models.ForeignKey('UsuarioPersonalizado', on_delete=models.PROTECT, null=True,
                                related_name='contacto_emergencia_relacionado')

    def __str__(self):
        return f'Nombre: {self.nombre_contacto_emergencia}, Numero: {self.numero_contacto_emergencia}'


class FichaMedica(models.Model):
    tipo_sangre = models.CharField(max_length=3)
    alergias = models.CharField(max_length=300, default='')
    enfermedades_cronicas = models.CharField(max_length=255, default='')
    usuario = models.ForeignKey('UsuarioPersonalizado', on_delete=models.PROTECT, null=True,
                                related_name='ficha_medica_relacionada')

    def __str__(self):
        return f'Tipo sangre: {self.tipo_sangre}' \
               f'Alergias: {self.alergias}' \
               f'Enfermedades: {self.enfermedades_cronicas}'


class Credencial(models.Model):
    estado_credencial = models.CharField(max_length=10, choices=[('activa', 'Activa'), ('inactiva', 'Inactiva')],
                                         default='inactiva')
    clave_credencial = models.CharField(max_length=36, unique=True)
    usuario = models.ForeignKey('UsuarioPersonalizado', on_delete=models.PROTECT, null=True,
                                related_name='credencial_relacionada')

    def __str__(self) -> str:
        return self.clave_credencial

    def save(self, *args, **kwargs):
        if not self.clave_credencial:
            self.clave_credencial = str(uuid.uuid4())
        super().save(*args, **kwargs)


# Clase que hereda de BaseUserManager, BaseUserManager tiene los datos necesarios para la construccion
# de un usuario, es necesaria para crear una clase usuaria desde cero, es como el esquelo pricipal
class UsuarioBasePersonalizado(BaseUserManager):
    def create_user(self, email, password=None, **campos_extra):
        if not email:
            raise ValueError("El campo email no debe estar vacio")
        email = self.normalize_email(email)
        user = self.model(email=email, **campos_extra)
        user.set_password(password)
        user.save()

    def create_superuser(self, email, password=None, **campos_extra):
        campos_extra.setdefault('is_staff', True)
        campos_extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **campos_extra)


# Esta clase sirve para agregar los campos necesarios para el modelo, Hace uso de dos clases:
#     AbstractBaseUser,
#     PermissionsMixin
# el primero nos permite agregar campos personalizados además de establecer el username field
# el segundo nor permite agregarle la funcionalidad de autenticacion
class UsuarioPersonalizado(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, error_messages={'unique': 'Ya existe un usuario con ese correo'})
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(null=True)
    direccion = models.CharField(max_length=255)
    usuario_activo = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    numero_telefono = models.CharField(max_length=10, null=True)
    imagen = CloudinaryField('image')

    # Relaciones entre tablas de usuario
    credencial = models.ForeignKey(Credencial, on_delete=models.PROTECT, null=True, related_name='credencial')
    ficha_medica = models.ForeignKey(FichaMedica, on_delete=models.PROTECT, null=True, related_name='ficha_medica')
    contacto_emergencia = models.ForeignKey(ContactoEmergencia, on_delete=models.PROTECT, null=True,
                                            related_name='contacto_emergencia_relacion')
    solicitud = models.ForeignKey('SolicitudCredencial', on_delete=models.PROTECT, null=True,
                                  related_name='solicitud_relacion')
    tipo_usuario = models.CharField(max_length=20, choices=[('alumno', 'alumno'), ('maestro', 'maestro'), ('administrador', 'administrador'), ('directivo', 'directivo')])

    objects = UsuarioBasePersonalizado()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # def nueva_solicitud(self):
    #     return self.solicitud = SolicitudCredencial.objects.create(usuario=self)

    def estado_ultima_solicitud(self):
        ultima_solicitud = self.solicitudes.order_by('-fecha_solicitud').first()
        estado = ultima_solicitud.estado_solicitud
        return estado

    def ficha_medica_existe(self):
        if self.ficha_medica is None:
            return False
        return True

    def contacto_emergencia_existe(self):
        if self.contacto_emergencia is None:
            return False
        return True

    def obtener_ultima_solicitud(self):
        estado = self.solicitudes.order_by('-fecha_solicitud').first()
        return estado

    def estado_credencial(self):
        return self.credencial.estado_credencial

    def clean(self):
        super().clean()
        if self.email and not self.email.endswith("@uptapachula.edu.mx"):
            raise ValidationError(
                'Solo se permiten correos con el dominio "@uptapachula.edu.mx"'
            )

    def crearCredencial(self):
        self.credencial = Credencial.objects.create(usuario=self)
        self.save()

    def crearFichaMedica(self, tipo_sangre, alergias, enfermedades_cronicas):
        self.ficha_medica = FichaMedica.objects.create(tipo_sangre=tipo_sangre, alergias=alergias,
                                                       enfermedades_cronicas=enfermedades_cronicas, usuario=self)
        self.save()

    def crearContactoEmergencia(self, nombre, numero_telefono):
        self.contacto_emergencia = ContactoEmergencia.objects.create(nombre_contacto_emergencia=nombre, numero_contacto_emergencia=numero_telefono,
                                                                     usuario=self)
        self.save()

    def requiereLlenarFichaMedica(self):
        if self.ficha_medica:
            return False
        return True

    def requiereLlenarContactoEmergencia(self):
        if self.contacto_emergencia:
            return False
        return True


    def __str__(self):
        return self.email


class Alumno(UsuarioPersonalizado):
    matricula = models.CharField(max_length=6, unique=True,
                                 error_messages={'unique': 'Ya existe esta matricula en el sistema'})
    cuatrimestre = models.ForeignKey(Cuatrimestre, on_delete=models.PROTECT, related_name='cuatrimestre')
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='carrera')
    gradoDeEstudio = models.ForeignKey(GradoDeEstudio, on_delete=models.PROTECT, related_name='grado_de_estudio')
    is_alumno = models.BooleanField(default=True)



class Maestro(UsuarioPersonalizado):
    especialidad = models.CharField(max_length=50)
    is_maestro = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Administrador(UsuarioPersonalizado):
    departamento = models.CharField(max_length=30)
    is_admin = models.BooleanField(default=False)
    is_administrador = models.BooleanField(default=True)

    def hacerAdmin(self):
        self.is_superuser = True
        self.save()

    def __str__(self):
        return self.nombre


class Directivo(UsuarioPersonalizado):
    puesto = models.CharField(max_length=30)
    is_directivo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class SolicitudCredencial(models.Model):
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD)
    tipo_solicitud = models.CharField(max_length=20, choices=TIPO_SOLICITUD)
    usuario = models.ForeignKey('UsuarioPersonalizado', on_delete=models.CASCADE, related_name='solicitudes')

    def __str__(self):
        return self.tipo_solicitud
