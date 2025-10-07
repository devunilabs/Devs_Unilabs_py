# Django Rest
from rest_framework import serializers
from modules.information.models import Information


class InformationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Information
        fields = ('key', 'value')


