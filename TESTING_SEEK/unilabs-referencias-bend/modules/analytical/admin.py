from django.contrib import admin
from modules.analytical.models import Analytical, StageAnalytical, StagePageAnalytical, VideoAnalytical
from simple_history.admin import SimpleHistoryAdmin


class VideoAnalyticalAdminInline(admin.TabularInline):
    model = VideoAnalytical
    extra = 0
    ordering = ('-id',)


class StageAnalyticalAdminInline(admin.TabularInline):
    model = StageAnalytical
    extra = 0
    ordering = ('-id',)


@admin.register(Analytical)
class AnalyticalAdmin(SimpleHistoryAdmin):
    inlines = [VideoAnalyticalAdminInline, StageAnalyticalAdminInline]
    ordering = ('-id',)


@admin.register(StagePageAnalytical)
class StagePageAnalyticalAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'stage', 'order')
    search_fields = ['stage', ]
    list_filter = ['stage', ]
    ordering = ('-id',)
    list_per_page = 50

