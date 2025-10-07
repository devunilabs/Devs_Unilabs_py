from django.contrib import admin
from modules.information.models import Information, Emails
from simple_history.admin import SimpleHistoryAdmin


@admin.register(Information)
class InformationAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'key', 'value')


@admin.register(Emails)
class EmailsAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'subject', 'emails')

    class Media:
        js = ('js/emails.js',)

    def has_add_permission(request, obj):
        return not Emails.objects.exists()

