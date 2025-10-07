from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send(data, to, template, subject):
    mail = EmailMessage(
        to=[to],
        subject=subject,
        body=render_to_string(template, data)
    )
    mail.content_subtype = 'html'
    mail.send()

