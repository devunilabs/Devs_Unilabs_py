# Rest framework
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db.models import Count

# Models
from .models import Analytical, StagePageAnalytical, PageSearchRecord

# Serializer
from .serializer import AnalyticalModelSerializer, StagePageCompleteModelSerializer, PageSearchRecordModelSerializer

# Django
from django.db.models import Q


class AnalyticalViewSet(viewsets.ModelViewSet):
    serializer_class = AnalyticalModelSerializer
    queryset = Analytical.objects.all()
    lookup_field = 'id'
    http_method_names = ['get', 'post']

    def paginate_queryset(self, queryset, view=None):
        return None

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        q = self.request.query_params.get('q', None)
        queryset = StagePageAnalytical.objects.all()

        if q:
            queryset = queryset.order_by('id').filter(
                Q(title__unaccent__icontains=q) |
                Q(description__unaccent__icontains=q) |
                Q(nota__unaccent__icontains=q) |
                Q(description_image__unaccent__icontains=q) |
                Q(stage__title__unaccent__icontains=q)
            )
        serializer = StagePageCompleteModelSerializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def record(self, request):
        data = request.data
        data['creator'] = request.user.id

        serializer = PageSearchRecordModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def last_searches(self, request):
        queryset = PageSearchRecord.objects.values('title', 'page').filter(creator_id=request.user.id).annotate(
            rows_qty=Count('page')).order_by('-rows_qty')[:3]

        serializer = PageSearchRecordModelSerializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StagePageViewSet(viewsets.ModelViewSet):
    serializer_class = StagePageCompleteModelSerializer
    queryset = StagePageAnalytical.objects.all().order_by('id')
    lookup_field = 'id'
    http_method_names = ['get', ]

