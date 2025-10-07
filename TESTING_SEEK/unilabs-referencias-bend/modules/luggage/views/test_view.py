
# Rest framework
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

# Models
from modules.luggage.models import LuggageDetail, Test, TestSearchRecord

# Serializer
from modules.luggage.serializers.test_serializer import TestAddModelSerializer, TestModelSerializer, \
    TestSearchRecordModelSerializer, TestUnilabsSerialiser
from modules.luggage.serializers.log_serializer import SuperLogAddModelSerializer

# Django
from django.conf import settings
from django.db.models import Q, Count
import requests
from datetime import datetime


class TestViewSet(viewsets.ModelViewSet):
    serializer_class = TestModelSerializer
    queryset = Test.objects.all().order_by('-created')
    lookup_field = 'id'

    @action(detail=False, methods=['GET'])
    def info(self, request):
        status_code = 200
        code = self.request.query_params.get('code', None)
        response = requests.get(settings.API_INTEGRATION_DOMAIN + "/prueba/detalle/{0}".format(code),
                                auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION), timeout=30)
        data = response.json()
        if response.status_code >= 400:
            status_code = response.status_code
            data = []
        return Response(data, status=status_code)

    def create(self, request, *args, **kwargs):
        data = request.data
        detail = LuggageDetail.objects.get(pk=data['detail'])
        data['patient'] = detail.patient_id
        data['luggage'] = detail.luggage_id
        serializer = TestAddModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        """LOG"""
        data['creator'] = request.user.id
        data['test'] = serializer.data['id']
        data['test_code'] = data['code']
        data['test_name'] = data['name']
        data['number_tubes'] = detail.luggage.number_tubes
        data['name'] = detail.patient.name
        data['first_surname'] = detail.patient.first_surname
        data['last_surname'] = detail.patient.last_surname
        data['gender'] = detail.patient.gender
        data['document_type'] = detail.patient.document_type
        data['document'] = detail.patient.document
        data['complete'] = detail.patient.complete
        data['date_birth'] = detail.patient.date_birth

        log = SuperLogAddModelSerializer(data=data)
        log.is_valid(raise_exception=True)
        self.perform_create(log)

        data = serializer.data
        return Response({"status": True, "data": data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = self.get_object()
        serializer = TestModelSerializer(data, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        """LOG"""
        data_log = request.data
        data_log['creator'] = request.user.id
        data_log['test_code'] = data_log['code']
        data_log['test_name'] = data_log['name']
        data_log['detail'] = serializer.data['detail']
        data_log['patient'] = serializer.data['patient']
        data_log['name'] = data.patient.name
        data_log['first_surname'] = data.patient.first_surname
        data_log['last_surname'] = data.patient.last_surname
        data_log['gender'] = data.patient.gender
        data_log['document_type'] = data.patient.document_type
        data_log['document'] = data.patient.document
        data_log['complete'] = data.patient.complete
        data_log['date_birth'] = data.patient.date_birth

        data_log['luggage'] = serializer.data['luggage']
        log = SuperLogAddModelSerializer(data=data_log)
        log.is_valid(raise_exception=True)
        self.perform_create(log)

        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = self.request.query_params.get('q', None)
        serializer = []
        status_code = status.HTTP_200_OK

        if not q:
            return Response({"message": "Se requiere un parámetro de búsqueda."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.get(
                f"{settings.API_INTEGRATION_DOMAIN}/pruebas/descripcion/{q}",
                auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION),
                timeout=30
            )

            # Si la API responde con un error, devuelve un mensaje adecuado
            if response.status_code != 200:
                return Response(
                    {"message": f"Error al obtener datos de la API externa (código {response.status_code})."},
                    status=response.status_code
                )

            data = response.json()
            print('response: ', data)
            if 'data' not in data or not data['data']:
                return Response({"message": "No se encontraron resultados."}, status=status.HTTP_400_BAD_REQUEST)

            # Serializa la respuesta
            serializer = TestUnilabsSerialiser(instance=data['data'], many=True, read_only=True).data

        except requests.exceptions.Timeout:
            return Response({"message": "La solicitud a la API externa ha excedido el tiempo de espera."},
                            status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({"message": f"Error de conexión: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Error inesperado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer, status=status_code)

    @action(detail=False, methods=['post'])
    def record(self, request):
        data = request.data
        data['creator_id'] = request.user.id

        serializer = TestSearchRecordModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def last_searches(self, request):
        queryset = TestSearchRecord.objects.values('code', 'name').filter(creator_id=request.user.id).annotate(
            rows_qty=Count('code')).order_by('-rows_qty')[:3]

        serializer = TestSearchRecordModelSerializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        test = Test.objects.filter(id=self.kwargs['id']).first()
        if test:
            """LOG"""
            data_log = {
                "creator": request.user.id,
                "name": test.patient.name,
                "first_surname": test.patient.first_surname,
                "last_surname": test.patient.last_surname,
                "gender": test.patient.gender,
                "document_type": test.patient.document_type,
                "document": test.patient.document,
                "date_birth": test.patient.date_birth,
                "test_code": test.code,
                "test_name": test.name,
                "comment": test.comment,
                "luggage": test.luggage.id,
                "detail": test.detail.id,
                "patient": test.patient.id,
                "deleted_at_test": datetime.now()
            }
            log = SuperLogAddModelSerializer(data=data_log)
            log.is_valid(raise_exception=True)
            self.perform_create(log)

            test.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

