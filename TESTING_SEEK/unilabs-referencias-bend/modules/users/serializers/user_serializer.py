# Models
# user_serializer.py
from modules.users.models import User, UserSession, Reference

# Django Rest
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from drf_extra_fields.fields import Base64ImageField

# Django
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

# Serializers
from modules.users.serializers.reference_serializer import ReferencesSerializer
from modules.setting.serializer import ModuleModelSerializer
import re
from rest_framework.exceptions import ValidationError
from rest_framework_recaptcha.fields import ReCaptchaField
from rest_framework_simplejwt.tokens import RefreshToken


class SessionAddModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSession
        fields = ('user', 'reference_active')


class UserModelSerializer(serializers.ModelSerializer):
    origenes = ReferencesSerializer(many=False, read_only=True)
    references = serializers.SerializerMethodField()
    access = ModuleModelSerializer(many=True, read_only=True)

    def get_references(self, instance):
        instances = instance.references.filter(active=True)
        return ReferencesSerializer(instances, many=True, read_only=True).data

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'cellphone', 'document_number', 'origenes',
                  'references', 'onboarding', 'onboarding_finish', 'last_login', 'gender', 'access', 'update_password')


class UserMeModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'job', 'cellphone', 'document_number', 'update_password')


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(min_length=6, max_length=32)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Credenciales invalidas')

        if user.type == 'Unilabs':
            raise serializers.ValidationError('No tiene permisos suficientes para ingresar')

        if not user.is_active and not user.type == 'Referencia':
            raise serializers.ValidationError('Su usuario no está activo')

        if not user.email_activated:
            raise serializers.ValidationError('Su cuenta no ha sido activada')

        self.context['user'] = user
        return data

    def create(self, validated_data):
        refresh = RefreshToken.for_user(user=self.context['user'])
        # token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], str(refresh.access_token)


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'cellphone', 'email', 'document_number')


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(password=value)
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ReCaptchaSerializer(serializers.Serializer):
    recaptcha = ReCaptchaField()

