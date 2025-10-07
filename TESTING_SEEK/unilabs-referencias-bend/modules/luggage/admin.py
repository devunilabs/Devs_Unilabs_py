from django.contrib import admin
from modules.luggage.models import Luggage, LuggageDetail, LuggageAvailableCode, Patient, Test, SuperLog
from import_export.admin import ImportExportModelAdmin
from .resources import LuggageExportResource
from simple_history.admin import SimpleHistoryAdmin
from django.utils.safestring import mark_safe
from django_admin_inline_paginator.admin import TabularInlinePaginated
from rangefilter.filters import DateRangeFilter
from datetime import timedelta
from modules.luggage.serializers.log_serializer import SuperLogAddModelSerializer
from django.urls import path
from django.shortcuts import redirect, reverse
from django.contrib import messages
import requests
from django.conf import settings
from modules.luggage.rules_business.send_integration import resend

""" Tabular's"""


class SuperLogAdminInline(TabularInlinePaginated):
    model = SuperLog
    extra = 0
    ordering = ('-updated',)
    readonly_fields = ['luggage__code', 'luggage__created', 'detail__creator',
                       'luggage__date_completed', 'detail__id', 'patient__name', 'patient__gender',
                       'patient__document_type', 'patient__date_birth', 'patient__created',  'test__test_code',
                       'test__test_name', 'test__comment', 'detail__deleted_at', 'test__deleted_at'
                       ]
    per_page = 20
    fields = ['luggage__code', 'luggage__created', 'detail__creator',
              'luggage__date_completed', 'detail__id', 'patient__name', 'patient__gender', 'patient__document_type',
              'patient__date_birth', 'patient__created',  'test__test_code', 'test__test_name',
              'test__comment', 'detail__deleted_at', 'test__deleted_at']

    def luggage__code(self, obj):
        return mark_safe("<a href='/admin/luggage/luggage/{0}/change/'><u>{0}</u></a>".format(obj.luggage.id))
    luggage__code.short_description = 'Valija'

    def luggage__created(self, obj):
        return (obj.luggage.created - timedelta(hours=5, minutes=00)).strftime("%d %b %Y %H:%M:%S")
    luggage__created.short_description = 'Fec Valija'

    def detail__creator(self, obj):
        if obj.creator_fullname:
            return "{0} | {1}".format("ADMIN", obj.creator_fullname)
        else:
            return "{0} | {1}".format("API", obj.creator)
    detail__creator.short_description = 'Creador'

    def detail__deleted_at(self, obj):
        return (obj.deleted_at - timedelta(hours=5, minutes=00)).strftime("%d %b %Y %H:%M:%S") if obj.deleted_at else ''
    detail__deleted_at.short_description = '(del)Fec Pac'

    def test__deleted_at(self, obj):
        return (obj.deleted_at_test - timedelta(hours=5, minutes=00)).strftime("%d %b %Y %H:%M:%S") if obj.deleted_at_test else ''
    test__deleted_at.short_description = '(del)Fec Prueba'

    def luggage__date_completed(self, obj):
        return (obj.date_completed - timedelta(hours=5, minutes=00)).strftime("%d %b %Y %H:%M:%S") if obj.date_completed else ''
    luggage__date_completed.short_description = 'Fec comp.'

    def detail__id(self, obj):
        return obj.detail if obj.detail else ''
    detail__id.short_description = 'Detalle'

    def test__test_code(self, obj):
        return obj.test_code if obj.test_code else ''
    test__test_code.short_description = 'Test'

    def test__test_name(self, obj):
        return obj.test_name if obj.test_name else ''
    test__test_name.short_description = 'Nom'

    def test__comment(self, obj):
        return obj.comment if obj.comment else ''
    test__comment.short_description = 'Comentario'

    def patient__name(self, obj):
        return "{0} {1} {2}".format(obj.name if obj.name else '', obj.first_surname if obj.first_surname else '',
                                    obj.last_surname if obj.last_surname else '')
    patient__name.short_description = 'Pac'

    def patient__gender(self, obj):
        return obj.gender if obj.gender else ''
    patient__gender.short_description = 'Sexo'
    patient__gender.empty_value_display = ''

    def patient__document_type(self, obj):
        return "{0} - {1}".format(obj.document_type if obj.document_type else '', obj.document if obj.document else '')
    patient__document_type.short_description = 'Doc'

    def patient__date_birth(self, obj):
        return obj.date_birth.strftime("%d %b %Y")
    patient__date_birth.short_description = 'F. Nac'

    def patient__created(self, obj):
        return (obj.updated - timedelta(hours=5, minutes=00)).strftime("%d %b %Y %H:%M:%S")
    patient__created.short_description = 'Fec log'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class LuggageDetailAdminInline(TabularInlinePaginated):
    model = LuggageDetail
    extra = 0
    ordering = ('-created',)
    readonly_fields = ['custom__id', 'sent', 'code', 'patient__id', 'patient__fullname', 'patient__document_type', 'patient__document',
                       'response_integration', 'body_integration', 'resend_btn']
    fields = ['custom__id', 'sent', 'code', 'patient__id', 'patient__fullname', 'patient__document_type', 'patient__document',
              'response_integration', 'body_integration', 'resend_btn']
    per_page = 20

    def custom__id(self, obj):
        return mark_safe("<a href='/admin/luggage/luggagedetail/{0}/change/'><u>{0}</u></a>".format(obj.id))
    custom__id.short_description = 'ID'
    custom__id.allow_tags = True

    def patient__id(self, obj):
        return mark_safe("<a href='/admin/luggage/patient/{0}/change/'><u>{0}</u></a>".format(obj.patient.id))
    patient__id.short_description = 'ID PAC.'
    patient__id.allow_tags = True

    def resend_btn(self, obj):
        if obj.sent and obj.body_integration:
            return mark_safe("-")
        else:
            return mark_safe("<a href='/admin/luggage/luggage/{0}/resend/'><u>Enviar</u></a>".format(obj.id))
    resend_btn.short_description = 'Reenviar'
    resend_btn.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def patient__fullname(self, obj):
        return "{0} {1} {2}".format(obj.patient.name if obj.patient.name else '',
                                    obj.patient.first_surname if obj.patient.first_surname else '',
                                    obj.patient.last_surname if obj.patient.last_surname else '')
    patient__fullname.short_description = 'Nombres'

    def patient__document(self, obj):
        return obj.patient.document if obj.patient.document else ''
    patient__document.short_description = 'Documento'

    def patient__document_type(self, obj):
        return obj.patient.document_type if obj.patient.document_type else ''
    patient__document_type.short_description = 'Tipo doc.'


class LuggageTestsAdminInline(TabularInlinePaginated):
    model = Test
    extra = 0
    fk_name = 'luggage'
    ordering = ('-created',)
    readonly_fields = ['id__custom', 'patient__fullname', 'code', 'name', 'comment']
    fields = ['id__custom', 'patient__fullname', 'code', 'name', 'comment']
    per_page = 20

    def patient__fullname(self, obj):
        return "{0} {1} {2}".format(obj.patient.name if obj.patient.name else '',
                                    obj.patient.first_surname if obj.patient.first_surname else '',
                                    obj.patient.last_surname if obj.patient.last_surname else '')
    patient__fullname.short_description = 'Nombres'

    def id__custom(self, obj):
        return mark_safe("<a href='/admin/luggage/test/{0}/change/'><u>{0}</u></a>".format(obj.id))
    id__custom.short_description = 'ID'
    id__custom.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class LuggageDetailPatientAdminInline(admin.TabularInline):
    model = LuggageDetail
    extra = 0
    ordering = ('-created',)
    readonly_fields = ['id__custom', 'luggage__code', 'luggage__creator', 'response_integration', 'body_integration']
    fields = ['id__custom', 'luggage__code', 'luggage__creator', 'response_integration', 'body_integration']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def id__custom(self, obj):
        return mark_safe("<a href='/admin/luggage/detail/{0}/change/'><u>{0}</u></a>".format(obj.id))
    id__custom.short_description = 'ID'
    id__custom.allow_tags = True

    def luggage__code(self, obj):
        return "{0} | {1}".format(obj.luggage.id, obj.luggage.status)
    luggage__code.short_description = 'Valija'

    def luggage__creator(self, obj):
        return obj.luggage.creator.name
    luggage__creator.short_description = 'Creador'


class PatientTestAdminInline(admin.TabularInline):
    model = Test
    extra = 0
    ordering = ('-created',)
    readonly_fields = ['luggage__code', 'luggage__creator', 'test__test_code', 'test__test_name', 'test__comment',
                       'test__created']
    fields = ['luggage__code', 'luggage__creator', 'test__test_code', 'test__test_name', 'test__comment',
              'test__created']
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def luggage__code(self, obj):
        return mark_safe("<a href='/admin/luggage/luggage/{0}/change/'>{1} - {2}</a>"
                         .format(obj.luggage.id, obj.luggage.id, obj.luggage.status))
    luggage__code.short_description = 'Valija'
    luggage__code.allow_tags = True

    def luggage__creator(self, obj):
        return "{0} {1}".format(obj.luggage.creator.first_name, obj.luggage.creator.last_name)
    luggage__creator.short_description = 'Creador'

    def test__test_code(self, obj):
        return obj.code
    test__test_code.short_description = 'Test cod.'

    def test__test_name(self, obj):
        return obj.name
    test__test_name.short_description = 'Nombre'

    def test__comment(self, obj):
        return obj.comment
    test__comment.short_description = 'Comentario'

    def test__created(self, obj):
        return (obj.created - timedelta(hours=5, minutes=00)).strftime("%d %b %Y %H:%M:%S")
    test__created.short_description = 'Test creación'


""" Registers"""


@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_filter = [('created', DateRangeFilter), 'created', 'document_type']
    search_fields = ['id', 'document_type', 'document', 'name', 'first_surname', 'last_surname',
                     'creator__username', 'creator__first_name', 'creator__last_name', 'creator__email']
    list_display = ['id', 'name', 'first_surname', 'last_surname', 'document_type', 'document', 'date_birth', 'created']
    list_export = ('xls', 'csv')
    ordering = ('-created',)
    exclude = ('creator', 'updater', 'creator_fullname')
    inlines = [PatientTestAdminInline, SuperLogAdminInline]
    history_list_display = ['name', 'first_surname', 'last_surname', 'gender', 'document_type', 'document',
                            'date_birth']
    readonly_fields = ('complete', )
    list_per_page = 50

    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if change and form.changed_data:
            serializer = SuperLogAddModelSerializer(data={
                "creator_fullname": request.user.username,
                "patient": obj.id,
                "name": obj.name,
                "first_surname": obj.first_surname,
                "last_surname": obj.last_surname,
                "gender": obj.gender,
                "document_type": obj.document_type,
                "document": obj.document,
                "date_birth": obj.date_birth
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return super(PatientAdmin, self).save_model(request, obj, form, change)


@admin.register(Test)
class TestAdmin(SimpleHistoryAdmin):
    list_filter = ('code', )
    search_fields = ['code', 'patient__name', 'patient__document', 'luggage__id', 'patient__id']
    list_display = ('id', 'code', 'name', 'patient__fullname', 'luggage__data')
    ordering = ('-created',)
    readonly_fields = ('luggage', 'patient', 'detail', 'created')
    list_per_page = 50

    def patient__fullname(self, obj):
        return "{0} {1} {2}".format(
            obj.patient.name if obj.patient.name else '',
            obj.patient.first_surname if obj.patient.first_surname else '',
            obj.patient.last_surname if obj.patient.last_surname else '')
    patient__fullname.short_description = 'Paciente'

    def luggage__data(self, obj):
        return "id: {0} | estado: {1} | tubos: {2}".format(obj.luggage.id, obj.luggage.status, obj.luggage.number_tubes)
    luggage__data.short_description = 'Valija'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Luggage)
class LuggageAdmin(SimpleHistoryAdmin):
    list_filter = [('created', DateRangeFilter), ('date_completed', DateRangeFilter), 'status', 'creator', 'reference']
    list_display = ('id', 'reference', 'status', 'sent', 'number_tubes', 'creator', 'created', 'date_completed')
    search_fields = ['status', 'creator__first_name', 'creator__last_name' ,  'creator__username', 'creator__email', 'created']
    inlines = [LuggageDetailAdminInline, LuggageTestsAdminInline, SuperLogAdminInline]
    list_export = ('xls', 'csv')
    ordering = ('-created',)
    readonly_fields = ('sent', 'status')
    list_per_page = 50

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:pk>/resend/', self.admin_site.admin_view(self.my_view)),
        ]
        return my_urls + urls

    def my_view(self, request, pk):
        detail = LuggageDetail.objects.filter(id=pk).first()
        status = resend(detail)

        if status:
            details = LuggageDetail.objects.filter(luggage_id=detail.luggage.id, sent=False)

            if len(details) == 0:
                luggage = Luggage.objects.filter(id=detail.luggage.id).first()
                luggage.sent = True
                luggage.save()

            self.message_user(request, "Se reenvió el análisis y se aceptó en Unilabs.", messages.SUCCESS)
        else:
            self.message_user(request, "Se reenvió el análisis, pero fue rechazado por Unilabs.", messages.ERROR)

        return redirect(reverse("admin:luggage_luggage_change", args=[detail.luggage.id]))

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LuggageDetail)
class LuggageDetailAdmin(SimpleHistoryAdmin):
    search_fields = ['luggage__status', 'luggage__creator__first_name', 'luggage__creator__last_name', 'luggage__creator__username',
                     'luggage__creator__email', 'patient__name', 'patient__first_surname', 'patient__last_surname']
    list_filter = [('created', DateRangeFilter), 'sent']
    list_display = ('id', 'code', 'patient__fullname', 'sent', 'luggage__data', 'created')
    resource_class = LuggageExportResource
    list_export = ('xls', 'csv')
    ordering = ('-created',)
    list_per_page = 50

    def patient__fullname(self, obj):
        return "{0} {1} {2}".format(obj.patient.name, obj.patient.first_surname, obj.patient.last_surname)
    patient__fullname.short_description = 'Paciente'

    def luggage__data(self, obj):
        return "id: {0} | estado: {1} | tubos: {2}".format(obj.luggage.id, obj.luggage.status, obj.luggage.number_tubes)
    luggage__data.short_description = 'Valija'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(LuggageAvailableCode)
class LuggageAvailableAdmin(SimpleHistoryAdmin):
    ordering = ('-id',)
    fields = ('start', 'end')

    def get_readonly_fields(self, request, obj=None):
        code = LuggageAvailableCode.objects.first()
        if code:
            return ('start', )
        else:
            return super(LuggageAvailableAdmin, self).get_readonly_fields(request, obj)

    def has_add_permission(request, obj):
        return not LuggageAvailableCode.objects.exists()

    def save_model(self, request, obj, form, change):
        return super(LuggageAvailableAdmin, self).save_model(request, obj, form, change)