import datetime

from django.contrib import admin

from modules.users.models import Reference, ReferenceAdmin
from .models import UnilabsReport, Tracking
from io import BytesIO
from django import forms
from django.core.files.base import ContentFile
from .maker import ReportMaker
from rangefilter.filters import DateRangeFilter


class ReferencesReportForm(forms.ModelForm):
    class Meta:
        model = UnilabsReport
        fields = '__all__'

    def clean(self):
        self.instance.user = self.request.user
        _instance = UnilabsReport(**self.cleaned_data)
        maker = ReportMaker(_instance, self.instance.user)

        if not maker.validate_queryset():
            raise forms.ValidationError('No se encontró información bajo los criterios ingresados.')
        return super(ReferencesReportForm, self).clean()

    def save(self, commit=True, *args, **kwargs):
        self.instance.user = self.request.user

        """ Get data """
        today = datetime.datetime.now()
        sheet_name = str(today.strftime("%m-%d-%Y %H.%M.%S"))

        maker = ReportMaker(self.instance, self.instance.user)
        df = maker.get_report()

        """ Write excel """
        writer = BytesIO()
        df.to_excel(writer, sheet_name=sheet_name, merge_cells=True)
        writer.seek(0)

        """ Save in field """
        self.instance.file = ContentFile(content=writer.getvalue(), name='{0}.xlsx'.format(self.instance.name))
        return super(ReferencesReportForm, self).save(commit)


@admin.register(UnilabsReport)
class ReferenceReportAdmin(admin.ModelAdmin):
    list_filter = [('created', DateRangeFilter), 'type']
    list_display = ['name', 'created', 'type', 'type_date']
    search_fields = ['name']
    readonly_fields = ['file']
    form = ReferencesReportForm

    class Media:
        js = ('js/emails.js',)

    def has_change_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'reference':

            if request.user.type == 'Unilabs':
                kwargs['queryset'] = Reference.objects.all()
            else:
                ids = ReferenceAdmin.objects.filter(user=request.user.id).values_list('reference__id', flat=True)
                kwargs['queryset'] = Reference.objects.filter(id__in=ids)

        return super(ReferenceReportAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(ReferenceReportAdmin, self).get_form(request, **kwargs)
        form.request = request
        return form


@admin.register(Tracking)
class ResultTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'creator', 'created')
    list_filter = [('created', DateRangeFilter), 'type', 'creator']
    ordering = ('-created',)
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
