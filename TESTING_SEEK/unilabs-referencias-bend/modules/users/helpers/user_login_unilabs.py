from modules.users.models import Reference, User
from django.conf import settings
import requests


def _login_unilabs():
    payload = {"username": settings.USER_CRON, "password": settings.PASS_CRON}
    response = requests.post(settings.API_CRON + "/api/auth/login", json=payload, timeout=180)
    if response.status_code == 200:
        return response.json()['access_token'], True, payload
    else: 
        return response.text, False, payload
