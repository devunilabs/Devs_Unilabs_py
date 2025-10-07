# Django Rest
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework import serializers
from rest_framework_recaptcha.fields import ReCaptchaField


class AuthSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    origenes = serializers.CharField(max_length=12)
    username = serializers.CharField(max_length=200)
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        validate_password(password=value)
        return value


class ReCaptchaSerializer(serializers.Serializer):
    recaptcha = ReCaptchaField()

