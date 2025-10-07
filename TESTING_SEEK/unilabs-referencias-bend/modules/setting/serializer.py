# Django Rest
from rest_framework import serializers
from modules.setting.models import Module


class ModuleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = ('id', 'module', 'icon', 'title')
