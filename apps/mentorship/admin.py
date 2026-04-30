from django.contrib import admin

from .models import CourseMentor, MentorshipRequest


@admin.register(CourseMentor)
class CourseMentorAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'expertise', 'is_active', 'approved_by', 'created_at')
    search_fields = ('course__code', 'course__title', 'student__username', 'student__full_name', 'expertise')
    list_filter = ('is_active', 'created_at')


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = (
        'course',
        'requester',
        'mentor',
        'topic',
        'status',
        'preferred_datetime',
        'scheduled_datetime',
        'handled_by',
        'created_at',
    )
    search_fields = (
        'course__code',
        'course__title',
        'requester__username',
        'mentor__student__username',
        'topic',
    )
    list_filter = ('status', 'created_at', 'scheduled_datetime')
    readonly_fields = ('created_at', 'updated_at')