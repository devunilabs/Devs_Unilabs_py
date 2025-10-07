from modules.loggeduser.models import Reference
from modules.loggeduser.serializer import ReferenceModelSerializer
import requests
from django.conf import settings


class ReferenceUtil:

    @staticmethod
    def get_or_save(user, data):
        ids = []
        references = []
        for code in data['origenes']:
            reference = Reference.objects.filter(code=code).first()

            if reference:
                ids.append(reference.id)
                references.append({
                    "id": reference.id, "name": reference.name,
                    "code": reference.code,
                    "ruc": reference.ruc})
            else:

                head = {'Authorization': "{0} {1}".format("Bearer", user['access_token'])}
                response = requests.post(settings.API + "/v1/get_company", headers=head, json={"codigo": code})

                if response.status_code == 200:

                    response = response.json()
                    if 'success' in response and response['success']:
                        data = {
                            "name": response['data']['razon'],
                            "ruc": response['data']['ruc'],
                            "code": response['data']['codigo'],
                            "email": response['data']['email']
                        }

                        serializer = ReferenceModelSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        ids.append(serializer.data['id'])
                        references.append({"id": serializer.data['id'], "name": data['name'], "code": data['code']})
        if len(references) > 0:
            references.sort(key=lambda x: x.get('name'), reverse=False)
        return ids, references

