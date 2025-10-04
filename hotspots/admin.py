from django.contrib import admin
from .models import Hotspot

@admin.register(Hotspot)
class HotspotAdmin(admin.ModelAdmin):
    list_display = ('name', 'crash_count', 'total_injured', 'total_killed', 'severity_index')
    list_filter = ('created_at',)
    search_fields = ('name',)