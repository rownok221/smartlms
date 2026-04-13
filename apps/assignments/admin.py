from django.contrib import admin

from .models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'deadline', 'max_marks', 'created_by', 'created_at')
    search_fields = ('title', 'course__code', 'course__title')
    list_filter = ('deadline', 'created_at')
    ordering = ('deadline',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'submitted_at', 'last_updated_at')
    search_fields = ('assignment__title', 'assignment__course__code', 'student__username')
    list_filter = ('status', 'submitted_at')
    readonly_fields = ('submitted_at', 'last_updated_at')