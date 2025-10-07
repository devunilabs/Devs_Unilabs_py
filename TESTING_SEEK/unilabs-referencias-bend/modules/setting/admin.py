from django.contrib import admin
from modules.setting.models import Module
from adminsortable.admin import SortableAdmin


@admin.register(Module)
class ModuleAdmin(SortableAdmin):
    list_display = ('title', 'created')
    list_per_page = 50

