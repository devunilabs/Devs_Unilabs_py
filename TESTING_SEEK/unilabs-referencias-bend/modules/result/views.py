#views.py
from rest_framework import status, viewsets

# Django
from rest_framework.response import Response
import requests
import io as BytesIO
import base64
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import action
import json
import urllib.parse

# Serializers
from modules.report.serializer import TrackingModelSerializer

# Models
from modules.users.models import User


class ResultViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'])
    def pdf(self, request):
        sid = self.request.query_params.get('sid', None)
        date = self.request.query_params.get('date', None)

        """ Get PDF """
        payload = {
            "operation": {
                "valor": "respdf",
                "origen": "",
                "analisis": sid,
                "fecha": date
            }
        }
        b64content = requests.post("https://integraciones.unilabs.pe/ws2seek", 
                                   json=payload, 
                                   auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION),
                                   timeout=180).json()
        
        b64_string = b64content['status']['documento']
        b64_string_modificado = b64_string[3:]

        buffer = BytesIO.BytesIO()
        content = base64.b64decode(b64_string_modificado)
        buffer.write(content)

        """ Tracking """
        serializer = TrackingModelSerializer(data={
            "type": "result_pdf",
            "params": request.build_absolute_uri(),
            "creator": request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse(buffer.getvalue(), content_type='application/pdf')

    @action(detail=False, methods=['get'])
    def search(self, request):
        page = self.request.query_params.get('page', 1)
        reference = self.request.query_params.get('reference', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        status = self.request.query_params.get('status', None)
        limit = settings.REST_FRAMEWORK['PAGE_SIZE']

        status_list = {
            "0": "",
            "1": "PENDIENTE",
            "2": "EN PROCESO",
            "3": "VALIDADO"
        }
        status_get = status_list.get(status, "")

        payload = {
            "operation": {
                "valor": "ListadoPac",
                "origen": reference,
                "fechai": start,
                "fechaf": end,
                "pid":"",
                "sid": "",
                "nombre":"",
                "apellidos":"",
                "estado": status_get
            }
        }
        try:
            response = requests.post(
                'https://integraciones.unilabs.pe/ws2seek',
                json=payload,
                auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION),
                timeout=180
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=400)

        data = []
        # Verificar si el 'response_data' tiene la estructura esperada
        if "status" in response_data and "items" in response_data["status"]:
            items = response_data["status"]["items"]
            for row in items:
                data.append({
                    "id": row.get('id', 'N/A'),
                    "document": row.get('document', 'N/A'),
                    "fullname": row.get('fullname', 'N/A'),
                    "date": row.get('date', 'N/A'),
                    "status": row.get('status', 'N/A'),
                })

        total = len(data)
        next_page = None if int(page) * limit >= total else int(page) + 1
        previous_page = None if int(page) == 1 else int(page) - 1
        return Response({
            "count": total,
            "next": next_page,
            "previous": previous_page,
            "results": data
        }, status=200)
