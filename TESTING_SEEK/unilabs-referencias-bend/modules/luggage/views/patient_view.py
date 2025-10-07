
# Rest framework
import datetime

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

# Models
from modules.luggage.models import Patient, Luggage, LuggageDetail, Test
from modules.users.models import User

# Serializer
from modules.luggage.serializers.patient_serializer import PatientModelSerializer, PatientAddSerializer, \
    AutoCompleteReniecSerializer, AutoCompleteUnilabsSerializer
from modules.luggage.serializers.luggage_serializer import LuggageModelSerializer, LuggageUpdateModelSerializer, \
    LuggageDetailAddModelSerializer
from modules.luggage.serializers.log_serializer import SuperLogAddModelSerializer

# Django
from django.conf import settings
import requests

# Utils
from modules.luggage.rules_business.patient_complete import valid


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientModelSerializer
    queryset = Patient.objects.all().order_by('-created')
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'put']

    def create(self, request, *args, **kwargs):
        luggage = request.data['luggage_id']
        logged_user = User.objects.filter(id=request.user.id).first()
        
        if not logged_user.origenes:
            return Response({"status": False, "message": "El usuario no tiene ninguna referencia asociada, contacte con el administrador"}, status=400)

        if not luggage:
            """ Valid """
            active_luggage = Luggage.objects.filter(status='active', creator=request.user.id).first()
            if active_luggage:
                active_serializer = LuggageModelSerializer(instance=active_luggage, many=False)
                return Response({"status": False, "message": "Ya una valija activa", "data": active_serializer.data},
                                status=status.HTTP_400_BAD_REQUEST)

            """ Insert New luggage"""
            serializer = LuggageUpdateModelSerializer(
                data={"status": 'active', "creator": request.user.id, "reference": logged_user.origenes.code if logged_user.origenes else None})

            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            luggage = serializer.data['id']
        
        else:
            if Luggage.objects.filter(id=luggage, status='completed').first():
                return Response({"status": False, "message": "Está valija ya está completada"}, status=400)

        patient = Patient.objects.filter(document=request.data['document']).first()

        data = request.data
        data['complete'] = valid(data)

        if not patient or not request.data['document']:
            """ Insert New patient """
            data['creator'] = request.user.id
            serializer = PatientAddSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            patient = serializer.data['id']
        else:
            """ Update data patient """
            data['updater'] = request.user.id
            serializer = PatientAddSerializer(patient, data=data, partial=kwargs.pop('partial', False))
            serializer.is_valid(raise_exception=True)
            serializer.save()

            """ Insert patient """
            serializer = PatientModelSerializer(instance=patient)
            patient = serializer.data['id']

        """ Insert luggage detail"""
        serializer = LuggageDetailAddModelSerializer(data={
            "luggage": luggage,
            "patient": patient
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        luggage_detail = serializer.data

        """LOG"""
        data['creator'] = request.user.id
        data['luggage'] = luggage
        data['patient'] = patient
        data['detail'] = luggage_detail['id']
        log = SuperLogAddModelSerializer(data=data)
        log.is_valid(raise_exception=True)
        self.perform_create(log)

        data = {
            "luggage_id": luggage,
            "patient": patient,
            "detail": luggage_detail['id']
        }
        return Response({"status": True, "data": data}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        q = self.request.query_params.get('q', None)
        if q:
            return self.queryset.filter(document__contains=q).order_by('-created')
        return self.queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        patient = self.get_object()
        data = request.data
        data['complete'] = valid(data)
        detail_id = None
        status_log = True

        if data['document']:
            """ Validation unique patient in luggage """
            detail = LuggageDetail.objects.filter(patient__document=data['document'], luggage_id=data['luggage']).first()
            if detail:
                detail_id = detail.id

            if detail and (detail.patient_id != patient.id):
                return Response({"status": False, "message": "Este paciente se encuentra en la valija"}, status=400)

            """ Validation user in table """
            patient_exist = Patient.objects.filter(document=data['document']).exclude(id=patient.id).first()
            if patient_exist:
                """ Update this user"""
                serializer = PatientAddSerializer(patient_exist, data=data, partial=kwargs.pop('partial', False))
                serializer.is_valid(raise_exception=True)
                serializer.save()

                """ Update relationships """
                detail = LuggageDetail.objects.filter(luggage_id=data['luggage'], patient=patient.id).first()
                LuggageDetail.objects.filter(luggage_id=data['luggage'], patient=patient.id).update(patient=patient_exist.id)
                Test.objects.filter(luggage_id=data['luggage'], patient=patient.id).update(patient=patient_exist.id)
                detail_id = detail.id

                """LOG"""
                status_log = False
                data['creator'] = request.user.id
                data['luggage'] = request.data['luggage']
                data['patient'] = patient_exist.id
                data['detail'] = detail_id
                log = SuperLogAddModelSerializer(data=data)
                log.is_valid(raise_exception=True)
                self.perform_create(log)

                """ Clean document """
                data['document'] = ''

            else:
                serializer = PatientAddSerializer(patient, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        """LOG"""
        if status_log:
            data['creator'] = request.user.id
            data['luggage'] = request.data['luggage']
            data['patient'] = patient.id
            data['detail'] = detail_id
            log = SuperLogAddModelSerializer(data=data)
            log.is_valid(raise_exception=True)
            self.perform_create(log)

        return Response({"status": True, "data": {}}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def documents(self, request):
        return Response([
            {'dni': 'Dni'},
            {'passport': 'Pasaporte'},
            {'ce': 'Carnet de extranjeria'},
            {'rn': 'Recien nacido'},
            {'pn': 'Partida de nacimiento'},
            {'pdp': 'Paciente con datos protegidos'},
            {'ot': 'Otros'}
        ], status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        document = self.request.query_params.get('document', None)
        type = self.request.query_params.get('type', None)
        response = {}

        try:
            url = "{0}/paciente/pid/{1}".format(settings.API_INTEGRATION_DOMAIN, document)
            data = requests.get(url, auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION)).json()
            
            if data['success']:
                response = AutoCompleteUnilabsSerializer(instance=data['data'], many=False, read_only=True).data
            if not response and type == 'dni':
                url = "{0}/dni/{1}?token={2}".format(settings.URL_RENIEC, document, settings.TOKEN_RENIEC)
                data = requests.get(url).json()
                if 'success' not in data:
                    response = AutoCompleteReniecSerializer(instance=data, many=False, read_only=True).data

            return Response(response, status=200)
        except KeyError:
            return Response({}, status=400)

    @action(detail=False, methods=['get'])
    def search(self, request):
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search_test(self, request):
        return Response([], status=status.HTTP_200_OK)
