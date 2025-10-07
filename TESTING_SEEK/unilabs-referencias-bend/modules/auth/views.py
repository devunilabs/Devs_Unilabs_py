# Rest framework
from datetime import datetime

from django.core import serializers
from idna import unicode
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action

# Django
import requests
from django.conf import settings
from modules.loggeduser.models import LoggedUser
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.password_validation import validate_password

# Serializer
from modules.loggeduser.serializer import LoggedUserModelSerializer, SessionAddModelSerializer, ReferencesSerializer
from modules.setting.serializer import VisibleModuleModelSerializer
from .serializer import ChangePasswordSerializer, ReCaptchaSerializer

# Utils
from modules.loggeduser.classes.reference import ReferenceUtil
from modules.auth.classes.auth import AuthUtil

# Models
from modules.loggeduser.models import Reference
from modules.luggage.models import Luggage
from modules.setting.models import VisibleModule


class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = []
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        return False

    @action(detail=False, methods=['post'])
    def login(self, request, pk=True):
        if not settings.DEBUG:
            serializer = ReCaptchaSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"status": False, "message": "El código captcha no es el correcto"}, status=400)

        last_login = datetime.now()

        # Auth request
        data, user, response = AuthUtil.connection(request)

        if response.status_code == 200:

            if len(data['origenes']) == 0:
                return Response({"status": False,
                                 "message": "Usuario sin Referencia asociada. Contactar al administrador."},
                                status=400)

            # Insert references
            ids, references = ReferenceUtil.get_or_save(user, data)
            if len(references) == 0:
                return Response({"status": False,
                                 "message": "Usuario sin Referencia asociada. Contactar al administrador."},
                                status=400)

            # Get logged user before
            logged = LoggedUser.objects.filter(user_id=data['id']).first()

            if not logged:
                data['origenes'] = data['origenes'][0]
                serializer = LoggedUserModelSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                logged = serializer.save()

                for id in ids:
                    logged.references.add(id)

                # Get current reference assign
                current_reference = Reference.objects.filter(code=data['origenes'][0]).first()
                user['onboarding'] = False
                user['change_password'] = False

            else:
                """ Sync references """
                logged.references.clear()
                for id in ids:
                    logged.references.add(id)

                # Update user
                logged.last_login = last_login
                logged.save()

                user['onboarding'] = logged.onboarding
                user['change_password'] = logged.change_password

                # Get current reference assign
                current_reference = Reference.objects.filter(code=logged.origenes).first()

            current_reference = ReferencesSerializer(instance=current_reference, read_only=True, many=False)
            user['current_reference'] = current_reference.data

            # Session
            log = SessionAddModelSerializer(data={"logged_user": logged.id})
            log.is_valid(raise_exception=True)
            self.perform_create(log)

            # Access
            access = VisibleModule.objects.all()
            serializer = VisibleModuleModelSerializer(access, many=True, read_only=True)


            return Response({"status": True, "data": user, "references": references, "access": serializer.data},
                            status=response.status_code)
        else:
            return Response({
                "status": False, "message": "El usuario o contraseña es incorrecto", "error": response.text
            }, status=400)

    @action(detail=False, methods=['post'])
    def logout(self, request, pk=True):
        head = {'Authorization': request.headers['Authorization']}
        response = requests.post(settings.API + "/auth/logout", headers=head, timeout=30)
        return Response({"status": True, "data": response.json()}, status=response.status_code)

    @action(detail=False, methods=['post'])
    def refresh(self, request, pk=True):
        try:
            head = {'Authorization': request.headers['Authorization']}
            response = requests.post(settings.API + "/auth/refresh", headers=head, timeout=30)
            return Response({"status": True, "data": response.json()}, status=response.status_code)
        except:
            return Response({"status": False}, status=401)

    @action(detail=False, methods=['post'])
    def me(self, request, pk=True):
        head = {'Authorization': request.headers['Authorization']}
        response = requests.post(settings.API + "/auth/me", headers=head, timeout=30)
        access = VisibleModule.objects.all()
        serializer = VisibleModuleModelSerializer(access, many=True, read_only=True)
        if response.status_code >= 400:
            return Response({"status": False, "message": response.text}, status=401)

        response = response.json()
        logged = LoggedUser.objects.filter(user_id=response['id']).first()

        return Response(
            {"status": True, "data": response, 
            "change_password": logged.change_password, 
            "onboarding": logged.onboarding,
            "onboarding_finish": logged.onboarding_finish,
            "access": serializer.data
            },
            status=200)

    @action(detail=False, methods=['post'])
    def send_code(self, request, pk=True):
        if request.data["email"] == 'error@unilabs.com':
            return Response({"status": False}, status=200)
        else:
            mail = EmailMultiAlternatives(
                subject="Unilabs - Recuperar contraseña",
                bcc=[request.data["email"]],
                body=render_to_string("emails/forgot_send_code.html", {"code": '2469'})
            )
            mail.content_subtype = 'html'
            mail.send()
        return Response({"status": True}, status=200)

    @action(detail=False, methods=['post'])
    def valid_code(self, request, pk=True):
        if request.data["code"] == '2469':
            return Response({
                "status": True,
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"},
                status=200)
        return Response({"status": False, "token": None}, status=200)

    @action(detail=False, methods=['post'])
    def forgot(self, request, pk=True):
        return Response({"status": True}, status=200)


class UserLoggedViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['put'])
    def onboarding(self, request, pk=True):
        type = self.request.query_params.get('type', None)
        if type and type == 'finish':
            LoggedUser.objects.filter(user_id=request.user.id).update(onboarding_finish=True)
        else:
            user = LoggedUser.objects.filter(user_id=request.user.id).first()
            LoggedUser.objects.filter(user_id=request.user.id).update(onboarding=True, onboarding_count=user.onboarding_count + 1)
        return Response({"status": True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def references(self, request):
        user = LoggedUser.objects.filter(user_id=request.user.id).first()
        serializer = LoggedUserModelSerializer(instance=user, read_only=True)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=['put'])
    def reference(self, request, pk=True):
        status_code = status.HTTP_400_BAD_REQUEST
        if request.data['code']:

            if Reference.objects.filter(code=request.data['code']).first():
                Luggage.objects.filter(creator=request.user.id, status='active').update(reference=request.data['code'])
                LoggedUser.objects.filter(user_id=request.user.id).update(origenes=request.data['code'])
                status_code = status.HTTP_200_OK

        return Response(status=status_code)

    @action(detail=False, methods=['get'])
    def password_rules(self, request, pk=False):
        rules = [
            "Su contraseña debe contener al menos 8 caracteres.",
            "Su contraseña debe tener al menos una letra mayúscula, una minúscula, un número y uno de estos caracteres @!-_#&+",
            "Su contraseña no debe ser una clave utilizada comúnmente.",
            "Su contraseña no puede asemejarse tanto a su información personal."
        ]
        return Response({"status": True, "rules": rules}, status=200)

    @action(detail=False, methods=['post'])
    def change_password(self, request, pk=True):
        data = request.data
        password_current = request.data['password']
        email = request.data['email']

        data['password'] = data['password'][3:]
        data['password'] = data['password'][:len(data['password']) - 3]
        serializer = ChangePasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        payload = {
            "id": request.user.id,
            "newemail": request.data['email'],
            "pass": password_current
        }

        head = {'Authorization': request.headers['Authorization']}

        # Valid email
        response_email = requests.post("https://resultados.unilabs.pe/api/auth/get_user_by_email", headers=head,
                                 json={"email": email}, timeout=30)

        if response_email.status_code == 200:
            response_email = response_email.json()

            if 'success' in response_email and response_email['success']:
                if response_email['data']['id'] != request.user.id:
                    return Response({"status": False,
                                     "message": "El correo ya se encuentra registrado, por favor utilice otro"},
                                    status=400)
        else:
            return Response({"status": False,
                             "message": "No es posible procesar su requerimiento, por favor contacte con el administrador"},
                            status=400)

        # Change password
        response = requests.post("https://resultados.unilabs.pe/api/auth/change_pass_by_user_id", headers=head,
                                 json=payload, timeout=30)

        if response.status_code >= 400:
            return Response({"status": False, "message": "No es posible procesar su requerimiento, por favor contacte con el administrador"}, status=400)

        # Get data  
        head = {'Authorization': request.headers['Authorization']}
        response = requests.post(settings.API + "/auth/me", headers=head, timeout=30)
        access = VisibleModule.objects.all()
        serializer = VisibleModuleModelSerializer(access, many=True, read_only=True)
        if response.status_code > 400:
            return Response({"status": False, "message": response.text}, status=401)

        data = response.json()
        logged = LoggedUser.objects.filter(user_id=data['id']).first()
        logged.change_password = True
        logged.save()

        return Response(
            {"status": True, 
            "data": data, 
            "change_password": True, 
            "onboarding": logged.onboarding,
            "onboarding_finish": logged.onboarding_finish,
            "access": serializer.data},
            status=response.status_code)
