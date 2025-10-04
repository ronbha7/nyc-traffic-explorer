from django.contrib import admin
from .models import Crash

@admin.register(Crash)
class CrashAdmin(admin.ModelAdmin):
    list_display = ('crash_date', 'borough', 'latitude', 'longitude', 'number_of_persons_injured', 'number_of_persons_killed')
    list_filter = ('borough', 'crash_date')
    search_fields = ('borough', 'contributing_factor')