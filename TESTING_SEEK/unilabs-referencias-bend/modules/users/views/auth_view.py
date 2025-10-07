# Rest framework
#auth_view.py
from datetime import datetime

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

# Django
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import requests

# Models
from modules.users.models import User, Reference

# Serializers
from modules.users.serializers.user_serializer import UserLoginSerializer, UserModelSerializer, \
    SessionAddModelSerializer, ReCaptchaSerializer, ChangePasswordSerializer
from modules.users.helpers.user_login_unilabs import _login_unilabs
from modules.users.helpers.unilabs_equivalencies import _select_document_type

from modules.users.helpers import user_change_password
from modules.users.helpers.mails import _send_mail_error


class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = []
    authentication_classes = []

    @action(detail=False, methods=['post'])
    def login(self, request, pk=True):
        
        if not settings.DEBUG:
            serializer_recaptcha = ReCaptchaSerializer(data=request.data)
            if not serializer_recaptcha.is_valid():
                return Response({"status": False, "message": "El código captcha no es el correcto"}, status=400)

        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status = False
        refresh = None
        serializer_user = None
        user = User.objects.filter(username=request.data['username']).first()

        if user:
            refresh = RefreshToken.for_user(user)
            serializer_user = UserModelSerializer(instance=user, read_only=True, context={'request': request})
            user.last_login = datetime.now()
            user.save()

            # Add Session
            log = SessionAddModelSerializer(data={"user": user.id, "reference_active": user.origenes.id if user.origenes else None})
            log.is_valid(raise_exception=True)
            log.save()

            # References comentado el 03 -10-2025
            #references = User.objects.filter(id=user.id).values_list('references__code', flat=True)
            #if references:
            #    self.update_reference(references)


            status = True
            log.is_valid(raise_exception=True)
            self.perform_create(log)

        return Response({
            "status": status,
            "access_token": str(refresh.access_token) if refresh else '',
            "refresh_token": str(refresh) if refresh else '',
            "token_type": "bearer",
            "expires_in": 3600,
            "data": serializer_user.data if serializer_user else ''
        }, status=200)

    def update_reference(self, codes):
        data = []

        # Login
        token, status_login, payload = _login_unilabs()
        
        # Update reference
        if status_login:
            head = {'Authorization': "{0} {1}".format("Bearer", token)}

            for code in codes:
                response = requests.post(settings.API_CRON + "/api/v1/get_company", headers=head, json={"codigo": code})

                if response.status_code == 200:
                    reference = response.json()['data']
                    payload = {
                        'name': reference['razon_social'] if 'razon_social' in reference else None,
                        'ruc': reference['ruc'] if 'ruc' in reference else None,
                        'phone': reference['telefonos'] if 'telefonos' in reference else None,
                        'email': reference['email'] if 'email' in reference else None,
                        'address': reference['direccion'] if 'direccion' in reference else None,
                        'description_siglo': reference['descripcion_siglo'] if 'descripcion_siglo' in reference else None,
                        'name_manager': reference['representante'] if 'representante' in reference else None,
                        'last_name_manager': reference['representante'] if 'representante' in reference else None,
                        'document_type_manager': _select_document_type(reference['tipo_doc']),
                        'document_number_manager': reference['numero_doc'] if 'numero_doc' in reference else None,
                        'active': reference['estado'] if 'estado' in reference else 0,
                        'motive': reference['estado_motivo'] if 'estado_motivo' in reference else None
                    }
                    Reference.objects.update_or_create(code=code, defaults=payload)
                else:
                    data.append(code)
        return data

    @action(detail=False, methods=['post'])
    def refresh(self, request, pk=True):
        try:
            token = RefreshToken(request.data['refresh_token'])

            return Response({
                "data": {
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                },
                "status": True,
            }, 200)
        except Exception as e:
            return Response({"status": False, "message": "Token invalido"}, status=400)

    @action(detail=False, methods=['post'])
    def logout(self, request, pk=True):
        try:
            token = RefreshToken(request.data['refresh_token'])
            token.blacklist()
            return Response({
                "status": True
            }, 200)
        except Exception as e:
            return Response({"status": False, "message": "Token invalido"}, status=400)

    @action(detail=False, methods=['post'])
    def send_code(self, request, pk=True):
        status_error = 400
        email = None
        token = None

        if request.data["username"]:
            import jwt
            import random

            user = User.objects.filter(username=request.data["username"]).first()
            if user:
                status_error = 200
                email = self.mask(user.email)
                token = jwt.encode({"email": email}, "UnilabsJWT", algorithm="HS256")

                code = random.randint(1111,9999)

                mail = EmailMultiAlternatives(
                    subject="Unilabs - Recuperar contraseña",
                    bcc=[user.email],
                    body=render_to_string("emails/forgot_send_code.html", {"code": code})
                )
                mail.content_subtype = 'html'
                mail.send()

                user.code_activation = code
                user.token_activation = token
                user.save()

        return Response({"status": True, "email": email, "token": token, "message": "Usuario invalido"}, status=status_error)

    @action(detail=False, methods=['get'])
    def password_rules(self, request, pk=True):
        rules = [
            "Su contraseña debe contener al menos 8 caracteres.",
            "Su contraseña debe tener al menos una letra mayúscula, una minúscula, un número y uno de estos caracteres @!-_#&+",
            "Su contraseña no debe ser una clave utilizada comúnmente.",
            "Su contraseña no puede asemejarse tanto a su información personal."
        ]
        return Response({"status": True, "rules": rules}, status=200)

    @action(detail=False, methods=['post'])
    def valid_code(self, request, pk=True):
        user = User.objects.filter(token_activation=request.data["token"], code_activation=request.data["code"]).first()
        if user:
            return Response({"status": True}, status=200)
        return Response({"status": False, "message": "Código invalido"}, status=400)

    @action(detail=False, methods=['post'])
    def forgot(self, request, pk=True):
        serializer = ChangePasswordSerializer(data=request.data)
        user = User.objects.filter(token_activation=request.data["token"], code_activation=request.data["code"]).first()
        if serializer.is_valid() and user:
            user.token_activation = ''
            user.code_activation = ''

            user.set_password(serializer.data.get("new_password"))
            user.verify_token = None
            user.save()

            status_rs, response = user_change_password._change_password(user, serializer.data.get("new_password"))
            if not status_rs:
                _send_mail_error("No se pudo actualizar la contraseña", {"response": response, "payload": request.user})

            return Response({"message": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def activate_user(self, request, pk=True):
        user = User.objects.filter(token_activation=request.query_params["token"]).first()
        if user:
            user.is_active = True
            user.email_activated = True
            user.token_activation = None
            user.save()
        
            if request.query_params["type"] == "Referencia":
                url = str(settings.APP_DOMAIN_WEB + "/auth/forgot-password")
                return HttpResponseRedirect(url)
            else:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                url = str(settings.APP_DOMAIN + "/reset/" + uid + "/" + token)
                return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(str(settings.APP_DOMAIN_WEB))

    def mask(self, email_id):
        email = email_id.find('@')
        if email > 0:
            return email_id[0]+"*****"+email_id[email-1:]

