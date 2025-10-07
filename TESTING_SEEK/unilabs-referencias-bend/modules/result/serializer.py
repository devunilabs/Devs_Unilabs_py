# Django Rest
from rest_framework import serializers


class ResultModelSerializer(serializers.Serializer):
    name = serializers.CharField(source='nombres')

