# Rest framework
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings

# Django
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Serializers
from modules.users.serializers.user_serializer import ChangePasswordSerializer, ForgotPasswordSerializer

# Models
from modules.users.models import User
import secrets


class ForgotUserViewSet(viewsets.ModelViewSet):
    permission_classes = []
    authentication_classes = []
    serializer_class = ForgotPasswordSerializer

    @action(detail=False, methods=['post'])
    def password(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        user = User.objects.filter(email=request.data["email"]).first()

        if serializer.is_valid() and user:
            token = secrets.token_urlsafe(70)
            user.verify_token = token
            user.save()
            mail = EmailMessage(
                to=[user.email],
                subject="SEEK.PE | Recuperar contraseña",
                body=render_to_string("emails/user_reset_password.html", {"token": token})
            )
            mail.content_subtype = 'html'
            mail.send()
            return Response({"message": "E-mail enviado", "status": True}, status=status.HTTP_200_OK)
        return Response({"message": "E-mail invalido", "status": False}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify_token(self, request, *args, **kwargs):
        user = User.objects.filter(verify_token=request.data["token"]).first()
        if user:
            return Response({"message": "Usuario existe", "status": True}, status=status.HTTP_200_OK)
        return Response({"message": "Token expirado", "status": False}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def reset(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        user = User.objects.filter(verify_token=request.data["token"]).first()
        if serializer.is_valid() and user:
            user.set_password(serializer.data.get("new_password"))
            user.verify_token = None
            user.save()
            return Response({"message": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

