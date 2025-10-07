# Django Rest
from rest_framework import serializers
from modules.luggage.models import Test, TestSearchRecord


class TestModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = ('id', 'code', 'name', 'comment', 'created', 'luggage', 'patient', 'detail')


class TestUnilabsSerialiser(serializers.ModelSerializer):
    code = serializers.CharField(source='codigo')
    name = serializers.CharField(source='descripcion')
    area = serializers.CharField(source='AreaProceso')
    type = serializers.CharField(source='TipodeMuestra')

    class Meta:
        model = Test
        fields = ('code', 'name', 'area', 'type')


class TestSearchRecordModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestSearchRecord
        fields = ('code', 'name', 'creator_id')


class TestAddModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = ('id', 'code', 'name', 'comment', 'detail', 'patient', 'luggage')

