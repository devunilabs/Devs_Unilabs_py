# Django Rest
from rest_framework import serializers
from modules.luggage.models import SuperLog


class SuperLogAddModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperLog
        fields = ('luggage', 'code', 'status', 'number_tubes', 'creator', 'patient', 'name', 'first_surname', 'detail',
                  'last_surname', 'gender', 'document_type', 'document', 'complete', 'date_birth', 'test_code',
                  'test_name', 'comment', 'deleted_at', 'date_completed', 'deleted_at_test', 'creator_fullname')

