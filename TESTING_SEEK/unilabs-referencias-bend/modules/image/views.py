from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

# Django
import requests
from django.conf import settings
import io as BytesIO
import base64
from django.http import HttpResponse
from urllib.parse import quote

# Models
from modules.users.models import User

# Serializers
from modules.image.serializer import ImageRisModelSerializer
from modules.report.serializer import TrackingModelSerializer


class ImageViewSet(viewsets.ModelViewSet):
    data = []

    @action(detail=False, methods=['get'])
    def pdf(self, request):
        document_number = request.user.document_number if request.user.document_number else request.user.origenes.document_number_manager
        first_name = request.user.first_name if request.user.first_name else request.user.origenes.name
        cellphone = request.user.cellphone if request.user.cellphone else request.user.origenes.phone
        email = request.user.email if request.user.email else request.user.origenes.email
        
        if not document_number or not first_name or not cellphone or not email:
            return Response({"message": "Sus datos personales están incompletos, por favor contacte con el administrador"}, status=400)
        
        document_type = 'DNI'
        if request.user.document_type == 'CE':
            document_type = 'FCard'
        elif request.user.document_type == 'PASSPORT':
            document_type = 'Passport'

        response = requests.post(
            settings.API_IMAGE + "/requestReport?INTEGRATION_TOKEN={0}"
                                 "&REPORT_ID={1}"
                                 "&REQUEST_TYPE={2}"
                                 "&USER_TYPE={3}"
                                 "&USER_ID={4}"
                                 "&USER_NAME={5}"
                                 "&USER_PHONE={6}"
                                 "&USER_EMAIL={7}"
            .format(
                settings.API_TOKEN_IMAGE,
                self.request.query_params.get('report_id', None),
                "1",
                document_type,
                request.user.document_number,
                request.user.first_name,
                request.user.cellphone,
                request.user.email
            ), timeout=180).json()
        
        if response['BASEX64_REPORT']:
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response['BASEX64_REPORT'])
            buffer.write(content)

            """ Tracking """
            serializer_tracking = TrackingModelSerializer(data={
                "type": "image_pdf",
                "params": request.build_absolute_uri(),
                "creator": request.user.id,
            })
            serializer_tracking.is_valid(raise_exception=True)
            serializer_tracking.save()
            
            return HttpResponse(buffer.getvalue(), content_type='application/pdf')
        else:
            return Response({'message': response['ERROR_DESCRIPTION']}, status=400)

    @action(detail=False, methods=['get'])
    def modality(self, request):
        status_code = 200
        response = requests.post(
            settings.API_IMAGE + "/modalityList?INTEGRATION_TOKEN={0}".format(settings.API_TOKEN_IMAGE), timeout=180)
        self.data = response.json()
        if response.status_code >= 400:
            status_code = response.status_code
            self.data = []
        return Response(self.data, status=status_code)

    @action(detail=False, methods=['get'])
    def studies(self, request):
        self.modality(request)

        qty = self.request.query_params.get('qty', None)
        page = self.request.query_params.get('page', None)
        reference = self.request.query_params.get('reference', None)
        order = self.request.query_params.get('order', 'DESC')
        order_key = self.request.query_params.get('order_key', 'STUDY_DATE')
        modality = self.request.query_params.get('modality', '')
        description = quote(self.request.query_params.get('description', '').lstrip().rstrip())
        type = self.request.query_params.get('type', '')
        number = self.request.query_params.get('number', '')
        origins = ''
        limit = settings.REST_FRAMEWORK['PAGE_SIZE']

        if reference:
            if reference == 'all':
                references = User.objects.filter(id=request.user.id).values_list('references__code', flat=True)
                origins = ','.join(references)
            else:
                origins = reference

        date_start = self.request.query_params.get('start', '2022-01-01')
        date_end = self.request.query_params.get('end', '2025-12-31')
        page = page if page else 1
        rows = qty if qty else settings.REST_FRAMEWORK['PAGE_SIZE']
        from_rows = (int(page) - 1) * int(rows)

        response = requests.post(
            settings.API_IMAGE + "/searchStudies?INTEGRATION_TOKEN={0}"
                                 "&CUSTOMER_REFERENCE={1}"
                                 "&DATE_FROM={2}"
                                 "&DATE_TO={3}"
                                 "&MAX_NUM_RECORDS={4}"
                                 "&FROM_NUM_RECORDS={5}"
                                 "&STUDY_MODALITY={6}"
                                 "&STUDY_DESCRIPTION={7}"
                                 "&PATIENT_ID={8}"
                                 "&PATIENT_TYPE={9}"
                                 "&SORT_BY={10}"
                                 "&SORT_DIRECTION={11}"
            .format(settings.API_TOKEN_IMAGE, origins, date_start, date_end, rows, from_rows,
                    modality, description, number, type, order_key, order),
            timeout=180)
        data = response.json()
        if response.status_code >= 400:
            return Response([], status=400)

        serializer = ImageRisModelSerializer(data['STUDIES'], many=True, read_only=True, context={'modalities': self.data})

        next = None if int(page)+1 == int(data['TOTAL_IN_SEARCH']) else int(page)+1 if int(data['TOTAL_IN_SEARCH']) >= int(page)*limit else None
        previous = None if int(page)-1 == 0 else int(page)-1

        return Response({"count": data['TOTAL_IN_SEARCH'], "next": next, "previous": previous,
                         "results": serializer.data, "isSuccess": 'Success'}, status=200)

    @action(detail=False, methods=['get'])
    def viewfinder(self, request):
        document_number = request.user.document_number if request.user.document_number else request.user.origenes.document_number_manager
        first_name = request.user.first_name if request.user.first_name else request.user.origenes.name
        cellphone = request.user.cellphone if request.user.cellphone else request.user.origenes.phone
        email = request.user.email if request.user.email else request.user.origenes.email

        if not document_number or not first_name or not cellphone or not email:
            return Response({"message": "Sus datos personales están incompletos, por favor contacte con el administrador"}, status=400)
        
        status_code = 200

        document_type = 'DNI'
        if request.user.document_type == 'CE':
            document_type = 'FCard'
        elif request.user.document_type == 'PASSPORT':
            document_type = 'Passport'

        response = requests.post(
            settings.API_IMAGE + "/requestStudy?INTEGRATION_TOKEN={0}"
                                 "&STUDY_ID={1}"
                                 "&USER_TYPE={2}"
                                 "&USER_ID={3}"
                                 "&USER_NAME={4}"
                                 "&USER_PHONE={5}"
                                 "&USER_EMAIL=0".format(
                settings.API_TOKEN_IMAGE,
                self.request.query_params.get('study_id', None),
                document_type,
                request.user.document_number or '99999999',
                request.user.first_name or 'Seek',
                request.user.cellphone or '999999999',
                request.user.email or 'seek@seek.pe'
            ), timeout=180)

        data = response.json()
        if response.status_code >= 400:
            status_code = response.status_code
            data = []
        return Response(data, status=status_code)
