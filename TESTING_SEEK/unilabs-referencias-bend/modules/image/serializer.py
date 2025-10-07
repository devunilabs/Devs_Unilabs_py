# Django Rest
from rest_framework import serializers


class ImageModelSerializer(serializers.Serializer):
    name = serializers.CharField(source='nombres')


class ImageRisModelSerializer(serializers.Serializer):
    document_type = serializers.CharField(source='PATIENT_TYPE')
    document = serializers.CharField(source='PATIENT_ID')
    fullname = serializers.CharField(source='PATIENT_NAME')
    date = serializers.CharField(source='STUDY_DATE')
    date_receipt = serializers.CharField(source='STUDY_RECEIPT_DATE')
    study_id = serializers.CharField(source='STUDY_ID')
    modality = serializers.CharField(source='STUDY_MODALITY')
    modality_description = serializers.CharField(source='STUDY_DESCRIPTION')
    description = serializers.CharField(source='STUDY_DESCRIPTION')
    type_of_urgency = serializers.CharField(source='STUDY_URGENCY_TYPE')
    study_urgency = serializers.CharField(source='STUDY_URGENCY')
    report_exist = serializers.BooleanField(source='REPORT_EXIST')
    image_exist = serializers.BooleanField(source='IMAGES_EXIST')
    report_id = serializers.CharField(source='REPORT_ID')
    report_date = serializers.CharField(source='REPORT_DATE')
    report_urgent_findings = serializers.CharField(source='REPORT_URGENT_FINDINGS')


    def to_representation(self, instance):
        document_types = {"0": "DNI", "1": "CE", "2": "Passport"}
        urgency_types = {"0": "Normal", "1": "Preferencial", "2": "Urgente"}
        ret = super(ImageRisModelSerializer, self).to_representation(instance)
        is_list_view = isinstance(self.instance, list)

        if is_list_view:
            document_type = ret.pop('document_type', None)
            type_of_urgency = ret.pop('type_of_urgency', None)
            modalities_current = ret.pop('modality', None).split("\\")
            modalities = self.context['modalities']['modalities']
            data = []

            for modality in modalities_current:
                description = ''
                for row in modalities:
                    if row['MODALITY'] == modality:
                        description = row['MODALITY_DESCRIPTION']

                data.append(description or modality)

            extra_ret = {
                "modalities": data,
                "document_type": document_types[document_type] if document_type else '',
                "type_of_urgency": urgency_types[type_of_urgency] if type_of_urgency else ''
            }
            ret.update(extra_ret)
        return ret

