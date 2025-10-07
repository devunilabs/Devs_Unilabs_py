# Django Rest
from rest_framework import serializers
from modules.users.models import Reference


class ReferencesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Reference
        fields = ('id', 'name', 'ruc', 'code', 'phone', 'email', 'address', 'active', 'description_siglo')


class ReferenceModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='description_siglo')
    
    class Meta:
        model = Reference
        fields = ('id', 'name', 'code', 'ruc', 'email')


