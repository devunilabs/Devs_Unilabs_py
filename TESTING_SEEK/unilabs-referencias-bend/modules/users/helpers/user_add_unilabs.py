from django.conf import settings
import requests
from modules.users.helpers.unilabs_equivalencies import _select_document_type, _type_user, _set_gender
from modules.users.models import Reference, User
from modules.users.helpers.user_login_unilabs import _login_unilabs
import random


def _send_unilabs_create(user, form):
    token, status_login, payload = _login_unilabs()
    if status_login:
        refs = Reference.objects.filter(id__in=form.cleaned_data.get('references')).values_list('code', flat=True)
        head = {'Authorization': "{0} {1}".format("Bearer", token)}
        payload = {
            "tipo_usuario": _type_user(user.type),
            "email": user.email,
            "username": user.username,
            "tipo_doc": _select_document_type(user.document_type),
            "numero_doc": user.document_number,
            "nombre": user.first_name,
            "apellido": user.last_name,
            "celular": user.cellphone,
            "puesto": user.job,
            "sexo": _set_gender(user.gender),
            "contrasena": "{0}{1}{2}".format(random.randint(100, 999), form.cleaned_data.get('password1'), random.randint(100, 999)),
            "estado": 1,
            "referencias": list(refs)
        }

        response = requests.post(settings.API_CRON + "/api/v1/add_user", headers=head, json=payload)

        if response.status_code == 200:
            return True, response.json(), payload
        return False, response.text, payload
    return False, "No se pudo hacer login", "No se pudo hacer login"

def _send_unilabs_update(user, form):
    token, status_login, payload = _login_unilabs()
    if status_login:
        refs = Reference.objects.filter(id__in=form.cleaned_data.get('references')).values_list('code', flat=True)
        head = {'Authorization': "{0} {1}".format("Bearer", token)}
        payload = {
            "tipo_usuario": _type_user(user.type),
            "email": user.email,
            "username": user.username,
            "tipo_doc": _select_document_type(user.document_type),
            "numero_doc": user.document_number,
            "nombre": user.first_name,
            "apellido": user.last_name,
            "celular": user.cellphone,
            "puesto": user.job,
            "sexo": "H",
            "estado": 1,
            "referencias": list(refs)
        }
        
        response = requests.post(settings.API_CRON + "/api/v1/edit_user", headers=head, json=payload)

        if response.status_code == 200:
            return True, response.json(), payload
        return False, response.text, payload
    return False, "No se pudo hacer login", "No se pudo hacer login"
