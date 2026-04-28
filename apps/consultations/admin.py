from django.contrib import admin

from .models import ConsultationRequest


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'topic',
        'course',
        'student',
        'mode',
        'status',
        'preferred_datetime',
        'scheduled_datetime',
        'handled_by',
        'created_at',
    )
    search_fields = (
        'topic',
        'course__code',
        'course__title',
        'student__username',
        'student__full_name',
        'handled_by__username',
    )
    list_filter = ('status', 'mode', 'created_at', 'scheduled_datetime')
    readonly_fields = ('created_at', 'updated_at')