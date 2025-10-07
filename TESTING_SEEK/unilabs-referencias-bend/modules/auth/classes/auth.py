from django.conf import settings
import requests


class AuthUtil:

    @staticmethod
    def connection(request):
        payload = {"username": request.data["username"], "password": request.data["password"]}
        response = requests.post(settings.API + "/auth/login", json=payload, timeout=30)

        data = []
        user = {}

        if response.status_code == 200:
            user = response.json()
            user['onboarding'] = False
            head = {'Authorization': "{0} {1}".format("Bearer", user['access_token'])}
            data = requests.post(settings.API + "/auth/me", headers=head, timeout=30).json()
            data['user_id'] = data['id']

        return data, user, response

