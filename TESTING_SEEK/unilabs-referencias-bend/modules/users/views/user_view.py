# Rest framework
# user_view.py
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

# Serializers
from modules.users.serializers.user_serializer import ChangePasswordSerializer, UserModelSerializer

# Models
from modules.users.models import User, Reference
from modules.luggage.models import Luggage
from modules.users.helpers import user_change_password
from modules.users.helpers.mails import _send_mail_error


class UpdatePasswordViewSet(viewsets.ModelViewSet):
    serializer_class = ChangePasswordSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserModelSerializer

    @action(detail=False, methods=['post'])
    def me(self, request):
        employee_id = request.user.id
        user = User.objects.filter(id=employee_id).first()

        if user:
            serializer = UserModelSerializer(instance=user, read_only=True, context={'request': request})
            return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def references(self, request):
        user = User.objects.filter(id=request.user.id).first()
        serializer = UserModelSerializer(instance=user, read_only=True)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=['put'])
    def onboarding(self, request, pk=True):
        type = self.request.query_params.get('type', None)
        if type and type == 'finish':
            User.objects.filter(id=request.user.id).update(onboarding_finish=True)
        else:
            user = User.objects.filter(id=request.user.id).first()
            User.objects.filter(id=request.user.id).update(onboarding=True, onboarding_count=user.onboarding_count + 1)
        return Response({"status": True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def reference(self, request, pk=True):
        status_code = status.HTTP_400_BAD_REQUEST
        if request.data['code']:
            if Reference.objects.filter(code=request.data['code']).first():
                Luggage.objects.filter(creator=request.user.id, status='active').update(reference=request.data['code'])
                User.objects.filter(id=request.user.id).update(origenes=request.data['code'])
                status_code = status.HTTP_200_OK
        return Response(status=status_code)

    @action(detail=False, methods=['put'])
    def change_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            request.user.set_password(serializer.data.get("new_password"))
            request.user.save()

            status_rs, response = user_change_password._change_password(request.user, serializer.data.get("new_password"))
            if not status_rs:
                _send_mail_error("No se pudo actualizar la contraseña", {"response": response, "payload": request.user})

            return Response({"message": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_password(self, request, *args, **kwargs):
        data = request.data
        #data['new_password'] = data['new_password'][3:]
        #data['new_password'] = data['new_password'][:len(data['new_password']) - 3]
        serializer = ChangePasswordSerializer(data=data)

        email_used = User.objects.filter(email=data['email']).exclude(id=request.user.id).first()
        if email_used:
            return Response({"status": False,  "message": "El correo ya se encuentra registrado, por favor utilice otro"}, status=400)

        if serializer.is_valid():
            request.user.set_password(data['new_password'])
            request.user.email = str(data['email'])
            request.user.update_password = True
            request.user.save()

            status_rs, response = user_change_password._change_password(request.user, data['new_password'])
            if not status_rs:
                _send_mail_error("No se pudo actualizar la contraseña", {"response": response, "payload": request.user})
            
            serializer = UserModelSerializer(instance=request.user, read_only=True, context={'request': request})
            return Response({'status': True, 'data': serializer.data, "message": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def encrypt(self, request):
        from django.contrib.auth.hashers import make_password

        users = User.objects.filter(encript_password=True)
        for user in users:
            user.password = make_password(user.password)
            user.encript_password = False
            user.save()

        return Response([], status=200)
