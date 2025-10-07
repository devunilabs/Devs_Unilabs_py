# Django Rest
from rest_framework import serializers
from .models import Tracking


class ResultModelSerializer(serializers.Serializer):
    name = serializers.CharField(source='nombres')


class TrackingModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tracking
        fields = ('type', 'params', 'creator')

