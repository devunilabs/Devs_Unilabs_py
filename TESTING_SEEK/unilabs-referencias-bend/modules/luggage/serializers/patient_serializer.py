# Models
from modules.luggage.models import Patient

# Django Rest
from rest_framework import serializers


class PatientModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'first_surname', 'last_surname', 'gender', 'document_type', 'document', 'mobile_number',
                  'date_birth', 'complete', 'created')


class PatientAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'first_surname', 'last_surname', 'gender', 'document_type', 'document', 'mobile_number',
                  'date_birth', 'complete', 'creator', 'updater')


class AutoCompleteReniecSerializer(serializers.Serializer):
    name = serializers.CharField(source='nombres')
    first_surname = serializers.CharField(source='apellidoPaterno')
    last_surname = serializers.CharField(source='apellidoMaterno')
    gender = serializers.CharField(default='')
    date_birth = serializers.CharField(default='')
    mobile_number = serializers.CharField(default='')

    class Meta:
        model = Patient
        fields = ('name', 'first_surname', 'last_surname', 'gender', 'date_birth', 'mobile_number')


class AutoCompleteUnilabsSerializer(serializers.Serializer):
    name = serializers.CharField(source='nombres')
    first_surname = serializers.CharField(source='appaterno')
    last_surname = serializers.CharField(source='apmaterno')
    gender = serializers.CharField(source='sexo')
    date_birth = serializers.CharField(source='fnac')
    mobile_number = serializers.CharField(source='telefono')
    email = serializers.CharField(source='correo')

    class Meta:
        model = Patient
        fields = ('name', 'first_surname', 'last_surname', 'gender', 'date_birth', 'mobile_number', 'email')

