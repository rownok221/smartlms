from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User

from .forms import CourseForm
from .models import Course, CourseInstructor, Enrollment


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def is_instructor(user):
    return user.role == User.Role.INSTRUCTOR


def is_student(user):
    return user.role == User.Role.STUDENT


@login_required
def course_list(request):
    if is_admin(request.user):
        courses = Course.objects.all().prefetch_related('course_instructors__instructor', 'enrollments__student')
    elif is_instructor(request.user):
        courses = Course.objects.filter(
            course_instructors__instructor=request.user
        ).prefetch_related('course_instructors__instructor', 'enrollments__student').distinct()
    else:
        courses = Course.objects.filter(
            enrollments__student=request.user
        ).prefetch_related('course_instructors__instructor', 'enrollments__student').distinct()

    context = {
        'page_title': 'Courses',
        'courses': courses,
        'can_create_course': is_admin(request.user) or is_instructor(request.user),
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related('course_instructors__instructor', 'enrollments__student'),
        pk=pk
    )

    allowed = False

    if is_admin(request.user):
        allowed = True
    elif is_instructor(request.user):
        allowed = CourseInstructor.objects.filter(course=course, instructor=request.user).exists()
    elif is_student(request.user):
        allowed = Enrollment.objects.filter(course=course, student=request.user).exists()

    if not allowed:
        messages.error(request, 'You are not authorized to view this course.')
        return redirect('courses:course_list')

    instructors = CourseInstructor.objects.filter(course=course).select_related('instructor')
    students = Enrollment.objects.filter(course=course).select_related('student')

    context = {
        'course': course,
        'instructors': instructors,
        'students': students,
        'can_manage_course': is_admin(request.user) or is_instructor(request.user),
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_create(request):
    if not (is_admin(request.user) or is_instructor(request.user)):
        messages.error(request, 'You are not authorized to create a course.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()

            if is_instructor(request.user):
                CourseInstructor.objects.get_or_create(
                    course=course,
                    instructor=request.user
                )

            messages.success(request, 'Course created successfully.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = CourseForm()

    context = {
        'page_title': 'Create Course',
        'form': form,
    }
    return render(request, 'courses/course_detail.html', context)