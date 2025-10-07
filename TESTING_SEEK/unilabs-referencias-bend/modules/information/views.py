from rest_framework import viewsets
from rest_framework.response import Response

# Models
from modules.information.models import Information

# Serializer
from modules.information.serializer import InformationModelSerializer


class InformationViewSet(viewsets.ModelViewSet):
    permission_classes = []
    authentication_classes = []
    serializer_class = InformationModelSerializer
    queryset = Information.objects.all()
    lookup_field = 'id'

    def paginate_queryset(self, queryset, view=None):
        return None

    def list(self, request, *args, **kwargs):
        key = self.request.query_params.get('key', None)
        data = {}
        if key:
            queryset = Information.objects.filter(key=key).first()
            if queryset:
                serializer = InformationModelSerializer(instance=queryset)
                data = {
                    key: serializer.data['value']
                }
            return Response(data)
        serializer = InformationModelSerializer(instance=self.queryset, many=True)
        return Response(serializer.data)

