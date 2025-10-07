from modules.patient.models import ClientVerify
from modules.patient.serializers.client import ClientVerifyCreateSerializer


def assign_code(data):
    client = ClientVerify.objects.filter(document=data['document']).first()

    if client:
        code = client.code
    else:
        last = ClientVerify.objects.all().last()
        if last:
            code = client.code + 1
        else:
            code = 100000

        serializer = ClientVerifyCreateSerializer(data={
            'document': data['document'],
            'code': code
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

    return code

