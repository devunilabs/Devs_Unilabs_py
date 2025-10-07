from modules.users.helpers.user_login_unilabs import _login_unilabs
import requests
from django.conf import settings
import random


def _change_password(user, password):
    token, status_login, payload = _login_unilabs()
    if not status_login:
        return False, payload
    
    head = {'Authorization': "{0} {1}".format("Bearer", token)}
    payload = {
        "username": user.username,
        "newemail": user.email,
        "pass": "{0}{1}{2}".format(random.randint(100, 999), password, random.randint(100, 999))
    }
    response = requests.post(settings.API_CRON + "/api/auth/change_pass_by_user_id", headers=head, json=payload)

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text
