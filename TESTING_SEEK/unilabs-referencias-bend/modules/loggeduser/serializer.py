# Models
from modules.loggeduser.models import LoggedUser, UserSession, Reference

# Django Rest
from rest_framework import serializers


class ReferencesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reference
        fields = ('name', 'ruc', 'code', 'phone', 'email', 'address')


class LoggedUserModelSerializer(serializers.ModelSerializer):
    references = ReferencesSerializer(many=True, read_only=True)

    class Meta:
        model = LoggedUser
        fields = ('id', 'username', 'name', 'email', 'user_id', 'onboarding', 'origenes', 'references', 'change_password')


class LoggedUserUpdateModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoggedUser
        fields = ('onboarding', 'origenes')


class SessionAddModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSession
        fields = ('logged_user', )


class ReferenceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reference
        fields = ('id', 'name', 'code', 'ruc', 'email')


