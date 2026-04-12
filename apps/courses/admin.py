from django.contrib import admin

from .models import Course, CourseInstructor, Enrollment


class CourseInstructorInline(admin.TabularInline):
    model = CourseInstructor
    extra = 1


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'created_by', 'created_at')
    search_fields = ('code', 'title')
    list_filter = ('created_at',)
    inlines = [CourseInstructorInline, EnrollmentInline]


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