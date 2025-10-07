from import_export import resources
from .models import LuggageDetail
from import_export import fields
from modules.luggage.models import Test


class LuggageExportResource(resources.ModelResource):

    """Luggage"""
    code = fields.Field(attribute='code', column_name="Código")
    luggage__id = fields.Field(attribute='luggage__id', column_name="Valija")
    luggage__number_tubes = fields.Field(attribute='luggage__number_tubes', column_name="Contenedores")
    luggage__creator = fields.Field(attribute='luggage__creator__first_name', column_name="Creador")
    luggage__created = fields.Field(attribute='luggage__created', column_name="Fec. Creación")
    luggage__date_completed = fields.Field(attribute='luggage__date_completed', column_name="Fec. Completó")

    """Patient"""
    patient__name = fields.Field(attribute='patient__name', column_name="Nombre")
    patient__first_surname = fields.Field(attribute='patient__first_surname', column_name="Apellido Paterno")
    patient__last_surname = fields.Field(attribute='patient__last_surname', column_name="Apellido Materno")

    patient__gender = fields.Field(attribute='patient__gender', column_name="Sexo")
    patient__document_type = fields.Field(attribute='patient__document_type', column_name="Doc. Tipo")
    patient__document = fields.Field(attribute='patient__document', column_name="Documento")
    patient__date_birth = fields.Field(attribute='patient__date_birth', column_name="Fec. Nacimiento")

    """Detail"""
    sent = fields.Field(attribute='sent', column_name="Enviado")

    """Test"""
    test = fields.Field(column_name="Pruebas")
    created = fields.Field(attribute='created', column_name="Fec. registro")

    def dehydrate_test(self, detail):
        data = []
        tests = Test.objects.filter(detail_id=detail.id).values('name', 'code', 'comment')
        for test in tests:
            data.append("{0}: {1} - {2} | ".format(test['code'], test['name'], test['comment']))
        return ''.join(str(e) for e in data)

    def dehydrate_created(self, detail):
        return detail.created.strftime("%Y-%m-%d %H:%M:%S")

    def dehydrate_luggage__created(self, detail):
        if detail.luggage.created:
            return detail.luggage.created.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ''

    def dehydrate_luggage__date_completed(self, detail):
        if detail.luggage.date_completed:
            return detail.luggage.date_completed.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ''

    class Meta:
        model = LuggageDetail
        fields = ('code', 'luggage__id', 'luggage__number_tubes', 'luggage__creator', 'luggage__created',
                  'luggage__date_completed', 'patient__name', 'patient__first_surname', 'patient__last_surname',
                  'patient__gender', 'patient__document', 'patient__document_type', 'patient__date_birth', 'sent',
                  'test', 'created')

