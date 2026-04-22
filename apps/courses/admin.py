from django.contrib import admin

from .models import Announcement, Course, CourseInstructor, Enrollment


class CourseInstructorInline(admin.TabularInline):
    model = CourseInstructor
    extra = 1


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1


class AnnouncementInline(admin.TabularInline):
    model = Announcement
    extra = 0
    fields = ('title', 'is_pinned', 'posted_by', 'created_at')
    readonly_fields = ('posted_by', 'created_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'created_by', 'created_at')
    search_fields = ('code', 'title')
    list_filter = ('created_at',)
    inlines = [CourseInstructorInline, EnrollmentInline, AnnouncementInline]


@admin.register(CourseInstructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    list_display = ('course', 'instructor', 'assigned_at')
    search_fields = ('course__code', 'course__title', 'instructor__username')
    list_filter = ('assigned_at',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'enrolled_at')
    search_fields = ('course__code', 'course__title', 'student__username')
    list_filter = ('enrolled_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_pinned', 'posted_by', 'created_at')
    search_fields = ('title', 'course__code', 'course__title', 'posted_by__username')
    list_filter = ('is_pinned', 'created_at')