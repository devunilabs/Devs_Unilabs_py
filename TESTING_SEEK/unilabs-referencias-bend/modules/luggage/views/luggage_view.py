# Rest framework
#luggage_view.py
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

# Models
from modules.luggage.models import Luggage, LuggageDetail, LuggageAvailableCode
from modules.users.models import Reference, User

# Serializer
from modules.luggage.serializers.patient_serializer import PatientModelSerializer
from modules.luggage.serializers.luggage_serializer import LuggageModelSerializer, LuggageUpdateModelSerializer, \
    LuggageDetailUpdateModelSerializer, LuggageDetailModelSerializer
from modules.luggage.serializers.log_serializer import SuperLogAddModelSerializer
from modules.report.serializer import TrackingModelSerializer

# Django
from django.db.models import Q
from django.http import HttpResponse
from datetime import datetime
from drf_renderer_xlsx.mixins import XLSXFileMixin
import xlwt

# Utils
from utils.render import to_pdf
from modules.luggage.rules_business.send_integration import run


class LuggageViewSet(viewsets.ModelViewSet, XLSXFileMixin):
    serializer_class = LuggageModelSerializer
    queryset = Luggage.objects.all().order_by('-created')
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        date_start = self.request.query_params.get('date_start', None)
        date_end = self.request.query_params.get('date_end', None)
        status = self.request.query_params.get('status', None)
        q = self.request.query_params.get('q', None)
        reference_code = self.request.query_params.get('reference', None)
        queryset = self.queryset.filter(creator_id=self.request.user.id)

        if status:
            queryset = self.queryset.filter(status=status, creator_id=self.request.user.id)

        if reference_code:
            if reference_code == 'all':
                user = User.objects.filter(id=self.request.user.id).first()
                ids = user.references.values_list('code')
                queryset = self.queryset.filter(reference__in=ids)
            else:
                queryset = self.queryset.filter(reference=reference_code)

        if date_start and not date_end:
            queryset = queryset.filter(date_completed__range=[date_start+' 00:00:00', date_start+' 23:59:59'], creator_id=self.request.user.id)

        if date_end and not date_start:
            queryset = queryset.filter(date_completed__range=[date_end+' 00:00:00', date_end+' 23:59:59'], creator_id=self.request.user.id)

        if date_start and date_end:
            queryset = queryset.filter(date_completed__range=[date_start+' 00:00:00', date_end+' 23:59:59'], creator_id=self.request.user.id)

        if q:
            queryset = queryset.order_by('id').distinct('id').filter(
                Q(details__patient__name__icontains=q) |
                Q(details__patient__first_surname__icontains=q) |
                Q(details__patient__last_surname__icontains=q) |
                Q(details__patient__document__icontains=q) |
                Q(details__code__icontains=q)
            ).filter(creator_id=self.request.user.id)
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = self.get_object()
        serializer = LuggageUpdateModelSerializer(data, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        """LOG"""
        data_log = request.data
        data_log['luggage'] = data.id
        log = SuperLogAddModelSerializer(data=data_log)
        log.is_valid(raise_exception=True)
        self.perform_create(log)

        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finish(self, request, id, **kwargs):
        luggage = Luggage.objects.filter(id=id, status='active').first()

        if luggage:
            """ Valid complete fields """
            details = LuggageDetail.objects.filter(luggage=luggage.id).order_by('id')
            for detail in details:
                if not detail.patient.complete:
                    patient = PatientModelSerializer(instance=detail.patient, many=False)
                    return Response({"message": "El usuario no tiene los campos completos", "data": patient.data},
                                    status=status.HTTP_400_BAD_REQUEST)

            """ Send integration """
            run(luggage, details, request)

            """LOG"""
            data_log = request.data
            data_log['luggage'] = luggage.id
            data_log['status'] = 'completed'
            data_log['number_tubes'] = luggage.number_tubes
            data_log['date_completed'] = datetime.now()
            log = SuperLogAddModelSerializer(data=data_log)
            log.is_valid(raise_exception=True)
            self.perform_create(log)
        else:
            return Response({"message": "La valija no está disponible"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'id': id, 'code': luggage.id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def active(self, request, **kwargs):
        luggage = Luggage.objects.filter(status='active', creator_id=request.user.id).first()
        serializer = LuggageModelSerializer(instance=luggage, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, id, **kwargs):
        luggage = Luggage.objects.filter(status='completed', id=id, creator_id=request.user.id).first()

        if luggage:
            serializer = LuggageModelSerializer(instance=luggage, many=False)
            data = serializer.data
            data['count_details'] = len(data['details'])

            i = 1
            for detail in serializer.data['details']:
                detail['index'] = i
                i = i+1

            pdf = to_pdf('pdf/luggage.html', data)

            """ Tracking """
            serializer = TrackingModelSerializer(data={
                "type": "luggage_pdf",
                "params": request.build_absolute_uri(),
                "creator": request.user.id,
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return HttpResponse(pdf, content_type='application/pdf')
        else:
            return HttpResponse({}, status=404)

    @action(detail=True, methods=['get'])
    def download_excel(self, request, id, **kwargs):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="valija.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Valija')
        row_num = 0
        data = []
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['', 'Cod. Valija', 'Estado', 'Fec. de envio', 'N. Tubos', 'Código', '¿Enviado?',
                   'P. Nombre', 'A. Paterno', 'A. Materno', 'Genero', 'Celular', 'Tipo documento', 'Documento',
                   'Cumpleaños', 'Pruebas', 'RUC Ref.', 'Referencia']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        rows = Luggage.objects.filter(status='completed', id=id)
        serializer = LuggageModelSerializer(instance=rows, many=True)

        if not serializer.data:
            return HttpResponse({}, status=404)

        """ Armamos el body"""
        for row in serializer.data:
            for detail in row['details']:

                """ Test to string"""
                test_string = []
                for test in detail['test']:
                    test_string.append("{0}: {1} - {2} | ".format(test['code'], test['name'], test['comment']))

                data.append([
                    row['id'],
                    row['status'],
                    row['date_completed'],
                    row['number_tubes'],

                    detail['code'],
                    detail['sent'],
                    detail['patient']['name'],
                    detail['patient']['first_surname'],
                    detail['patient']['last_surname'],
                    'Hombre' if detail['patient']['gender'] == 'H' else 'Mujer',
                    detail['patient']['mobile_number'],
                    detail['patient']['document_type'],
                    detail['patient']['document'],
                    detail['patient']['date_birth'],
                    detail['patient']['mobile_number'],
                    ''.join(str(e) for e in test_string),
                    row['reference_ruc'],
                    row['reference_name']
                ])

        """ Llenamos el excel """
        for row in data:
            row_num += 1

            col_num = 0
            for value in row:
                col_num += 1
                ws.write(row_num, col_num, value, font_style)
        wb.save(response)

        """ Tracking """
        serializer = TrackingModelSerializer(data={
            "type": "luggage_excel",
            "params": request.build_absolute_uri(),
            "creator": request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response


class LuggageDetailViewSet(viewsets.ModelViewSet):
    serializer_class = LuggageDetailModelSerializer
    queryset = LuggageDetail.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        q = self.request.query_params.get('q', None)
        if not q:
            return self.queryset.filter(luggage__creator_id=self.request.user.id)
        else:
            return self.queryset.filter(Q(luggage__creator_id=self.request.user.id))\
                .filter(Q(patient__name__icontains=q) | Q(luggage__code__icontains=q))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = self.get_object()
        serializer = LuggageDetailUpdateModelSerializer(data, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        detail = LuggageDetail.objects.filter(id=self.kwargs['id']).first()
        if detail:
            """LOG"""
            data_log = request.data
            data_log['creator'] = request.user.id

            data_log['patient'] = detail.patient.id
            data_log['name'] = detail.patient.name
            data_log['first_surname'] = detail.patient.first_surname
            data_log['last_surname'] = detail.patient.last_surname
            data_log['gender'] = detail.patient.gender
            data_log['document_type'] = detail.patient.document_type
            data_log['document'] = detail.patient.document
            data_log['complete'] = detail.patient.complete
            data_log['date_birth'] = detail.patient.date_birth
            data_log['deleted_at'] = datetime.now()
            data_log['luggage'] = detail.luggage.id
            log = SuperLogAddModelSerializer(data=data_log)
            log.is_valid(raise_exception=True)
            self.perform_create(log)

            detail.delete()
        return Response(status=status.HTTP_200_OK)

