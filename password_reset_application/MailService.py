from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
import string
import secrets


class Reset:

    def __init__(self):
        pass

    def send(self, email, name) -> str:
        remitente = "sistemacredencializacion@gmail.com"
        destinatario = [email]
        asunto = "Restablecer Contraseña"
        password = self.__generate_password()
        html_message = render_to_string('received.html', {"password": password, "name": name})
        send_mail(asunto, strip_tags(html_message), remitente, destinatario, html_message=html_message)
        return password

    def __generate_password(self) -> str:
        character = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(character) for _ in range(10))
        return password
