from celery import shared_task

# Django
from django.conf import settings
import requests
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# Models
from modules.users.models import Reference, User, Synchronization
from modules.users.helpers.user_login_unilabs import _login_unilabs
from modules.information.models import Emails

@shared_task()
def references():
    token, status_login, payload = _login_unilabs()
    
    data = []
    if status_login:
        references = _get_references(token)
        if references:
            for reference in references:
                if not _create_or_update(reference):
                    data.append(reference)
        
        # Save in model Synchronization
        Synchronization.objects.create(is_ok=False if len(data) > 0 else True, type='Referencia', body=[], response=data)
    else:
        Synchronization.objects.create(is_ok=False, type='Referencia', body=payload, response=token)

def _get_references(token):
        head = {'Authorization': "{0} {1}".format("Bearer", token)}
        data = []
        response = requests.get(settings.API_CRON + "/api/v1/get_all_companies", headers=head, timeout=180)

        if response.status_code == 200:
            data = response.json()['data']
        return data

def _create_or_update(reference):
    status = False
    try:
        if 'codigo' in reference:
            status = True
            payload = {
                'name': reference['razon_social'] if reference['razon_social'] else None,
                'ruc': reference['ruc'] if reference['ruc'] else None,
                'code': reference['codigo'] if reference['codigo'] else None,
                'phone': reference['telefonos'] if reference['telefonos'] else None,
                'email': reference['email'] if reference['email'] else None,
                'address': reference['direccion'] if reference['direccion'] else None,
                'description_siglo': reference['descripcion_siglo'] if reference['descripcion_siglo'] else None,
                'name_manager': reference['representante'] if reference['representante'] else None,
                'last_name_manager': reference['representante'] if reference['representante'] else None,
                'document_type_manager': __select_document_type(reference['tipo_doc']) if reference['tipo_doc'] else '',
                'document_number_manager': reference['numero_doc'] if reference['numero_doc'] else None,
                'active': reference['estado'] if reference['estado'] else None,
                'motive': reference['estado_motivo'] if reference['estado_motivo'] else None
            }
            obj, created = Reference.objects.update_or_create(code=reference['codigo'], defaults=payload)
    except Exception as ex:
        status = False
    return status

def __select_document_type(value):
    response = ''
    if value == 1:
        response = 'Dni'
    elif value == 2:
        response = 'Carnet extranjeria'
    elif value == 3:
        response = 'Pasaporte'
    return response


@shared_task()
def users():
    emails = Emails.objects.filter(type='error_sync').values_list('emails', flat=True).first()
    if not emails:
        emails = ["peru.helpdesk@unilabs.com"]
    
    token, status_login, payload = _login_unilabs()
    data = []

    if status_login:
        users = _get_users(token)
        if users:
            for user in users:
                user['reasons'] = "Error en el registro"

                if user['name'] is None:
                    user['reasons'] = "El nombre no puede estar vacío"
                
                elif user['username'] is None:
                    user['reasons'] = "El username no puede estar vacío"
                else:
                    user['reasons'] = "El correo y el username deben ser únicos"

                if not _create_or_update_user(user):
                    data.append(user)
    
        if len(data) > 0:
            mail = EmailMultiAlternatives(
                subject="Usuarios no cargados",
                bcc=list(emails),
                body=render_to_string("emails/error_product_cron.html", {
                    "data": data
                })
            )
            mail.content_subtype = 'html'
            mail.send()
        Synchronization.objects.create(is_ok=False if len(data) > 0 else True, type='Usuarios', body=[], response=data)
    else:
        Synchronization.objects.create(is_ok=False, type='Usuarios', body=payload, response=token)

    print('users completed')

def _get_users(token):
    head = {'Authorization': "{0} {1}".format("Bearer", token)}
    data = []
    response = requests.get(settings.API_CRON + "/api/v1/get_all_users", headers=head, timeout=180)

    if response.status_code == 200:
        data = response.json()['data']
    return data

def _create_or_update_user(user):
    try:
        payload = {
            'type': __select_type_user(user['tipo_usuario']) if user['tipo_usuario'] else "Referencia",
            'username': user['username'] if user['username'] else None,
            'email': user['email'] if user['email'] else None,
            'first_name': user['name'] if user['name'] else None,
            'last_name': user['apellido'] if user['apellido'] else None,
            'job': user['puesto'] if user['puesto'] else None,
            'cellphone': user['celular'] if user['celular'] else None,
            'gender': user['sexo'] if user['sexo'] else None,
            'document_number': user['numero_doc'] if user['numero_doc'] else None,
            'document_type': __select_document_type(user['tipo_usuario']) if user['tipo_usuario'] else None,
            'email_activated': int(user['estado']) if user['estado'] else 0,
            'is_active': int(user['estado']) if user['estado'] else 0,
            'is_staff': int(user['estado']) if user['estado'] else 0,
        }
        obj, created = User.objects.update_or_create(username=user['username'], defaults=payload)
        if created:
            # Add modules
            obj.access.add(3)
            obj.access.add(4)
            obj.access.add(5)
            obj.access.add(7)

            # Add permissions
            obj.groups.add(1)

            obj.save()

        if user['referencias'] and len(user['referencias']) > 0:
            for reference in user['referencias']:
                ref_obj = Reference.objects.filter(code=reference).first()
                if ref_obj:
                    obj.references.add(ref_obj)
                    obj.save()
        status = True
    except Exception as ex:
        status = False
    return status

def __select_type_user(value):
    response = 1
    if value == 1:
        response = 'Referencia'
    elif value == 2:
        response = 'Unilabs'
    return response
