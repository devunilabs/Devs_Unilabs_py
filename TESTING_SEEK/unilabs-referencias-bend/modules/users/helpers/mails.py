from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.utils.encoding import force_bytes
from django.core.mail import send_mail


def _send_mail_activation(user, token):
    subject = "{0}".format("Activación de cuenta de usuario")
    email_template_name = "emails/password_reset_user.html"
    c = {
        "email": user.email,
        'domain': settings.APP_DOMAIN,
        'site_name': 'Unilabs',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,
        'protocol': 'https',
        'username': user.username,
        'type': user.type
    }
    email = render_to_string(email_template_name, c)
    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def _send_mail_error(subject, body):
    to = ["peru.helpdesk@unilabs.com"]
    email = render_to_string("emails/error_user_unilabs.html", body)
    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False)

