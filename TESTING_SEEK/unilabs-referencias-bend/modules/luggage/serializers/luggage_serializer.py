# Models
from modules.luggage.models import Luggage, LuggageDetail

# Django Rest
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

# Serializers
from modules.luggage.serializers.patient_serializer import PatientModelSerializer
from modules.luggage.serializers.test_serializer import TestModelSerializer


class LuggageDetailModelSerializer(serializers.ModelSerializer):
    test = serializers.SerializerMethodField()
    patient = PatientModelSerializer(many=False, read_only=True)
    test_total = serializers.SerializerMethodField()

    def get_test(self, instance):
        tests = instance.test.all().order_by('-created')
        return TestModelSerializer(tests, many=True, read_only=True).data

    def get_test_total(self, obj):
        return obj.test.count()

    class Meta:
        model = LuggageDetail
        fields = ('id', 'code', 'sent', 'patient', 'created', 'test', 'test_total')


class LuggageModelSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    patients_total = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    reference_name = serializers.SerializerMethodField()
    reference_ruc = serializers.SerializerMethodField()
    date_completed = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    def get_reference(self, instance):
        if instance.reference:
            return "{0} - {1}".format(instance.reference.ruc or '', instance.reference.name or '')
        else:
            return ''

    def get_reference_name(self, instance):
        if instance.reference:
            return instance.reference.name
        else:
            return ''

    def get_reference_ruc(self, instance):
        if instance.reference:
            return instance.reference.ruc or ''
        else:
            return ''

    def get_details(self, instance):
        details = instance.details.all().order_by('patient__complete', 'patient__name')
        return LuggageDetailModelSerializer(details, many=True, read_only=True).data

    def get_patients_total(self, obj):
        return obj.details.count()

    class Meta:
        model = Luggage
        fields = ('id', 'status', 'created', 'creator', 'number_tubes', 'image', 'details', 'date_completed',
                  'patients_total', 'reference', 'reference_name', 'reference_ruc')


class LuggageUpdateModelSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Luggage
        fields = ('id', 'image', 'number_tubes', 'creator', 'reference')


class LuggageDetailAddModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = LuggageDetail
        fields = ('id', 'luggage', 'patient')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('luggage', 'patient'),
                message="El paciente ya se encuentra registrado en esta valija"
            )
        ]


class LuggageDetailUpdateModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = LuggageDetail
        fields = ('test_code', 'test_name', 'comment')
