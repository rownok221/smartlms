from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User

from .forms import AnnouncementAttachmentForm, AnnouncementForm, CourseForm
from .models import Announcement, AnnouncementAttachment, Course, CourseInstructor, Enrollment


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def is_instructor(user):
    return user.role == User.Role.INSTRUCTOR


def is_student(user):
    return user.role == User.Role.STUDENT

def save_announcement_attachments(announcement, files, uploaded_by):
    for file in files:
        AnnouncementAttachment.objects.create(
            announcement=announcement,
            file=file,
            uploaded_by=uploaded_by
        )


@login_required
def course_list(request):
    if is_admin(request.user):
        courses = Course.objects.all().prefetch_related(
            'course_instructors__instructor',
            'enrollments__student',
            'announcements'
        )
    elif is_instructor(request.user):
        courses = Course.objects.filter(
            course_instructors__instructor=request.user
        ).prefetch_related(
            'course_instructors__instructor',
            'enrollments__student',
            'announcements'
        ).distinct()
    else:
        courses = Course.objects.filter(
            enrollments__student=request.user
        ).prefetch_related(
            'course_instructors__instructor',
            'enrollments__student',
            'announcements'
        ).distinct()

    context = {
        'page_title': 'Courses',
        'courses': courses,
        'can_create_course': is_admin(request.user) or is_instructor(request.user),
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'course_instructors__instructor',
            'enrollments__student',
            'announcements__posted_by'
        ),
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
    announcements = Announcement.objects.filter(course=course).select_related(
    'posted_by'
).prefetch_related('attachments')

    context = {
        'course': course,
        'instructors': instructors,
        'students': students,
        'announcements': announcements,
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
    return render(request, 'courses/course_form.html', context)


@login_required
def announcement_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not (is_admin(request.user) or CourseInstructor.objects.filter(course=course, instructor=request.user).exists()):
        messages.error(request, 'You are not authorized to post announcements for this course.')
        return redirect('courses:course_detail', pk=course.pk)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course = course
            announcement.posted_by = request.user
            announcement.save()

            save_announcement_attachments(
    announcement=announcement,
    files=form.cleaned_data.get('attachments', []),
    uploaded_by=request.user
)

            messages.success(request, 'Announcement posted successfully.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = AnnouncementForm()
        context = {
            'course': course,
            'form': form,
        }
        return render(request, 'courses/announcement_form.html', context)

@login_required
def announcement_attachment_add(request, pk):
    announcement = get_object_or_404(
        Announcement.objects.select_related('course', 'posted_by').prefetch_related('attachments'),
        pk=pk
    )
    course = announcement.course

    if not (is_admin(request.user) or CourseInstructor.objects.filter(course=course, instructor=request.user).exists()):
        messages.error(request, 'You are not authorized to add files to this announcement.')
        return redirect('courses:course_detail', pk=course.pk)

    if request.method == 'POST':
        form = AnnouncementAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            save_announcement_attachments(
                announcement=announcement,
                files=form.cleaned_data.get('attachments', []),
                uploaded_by=request.user
            )

            messages.success(request, 'Files added to announcement successfully.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = AnnouncementAttachmentForm()

    context = {
        'course': course,
        'announcement': announcement,
        'form': form,
    }
    return render(request, 'courses/announcement_attachment_form.html', context)

@login_required
def announcement_attachment_delete(request, pk):
    attachment = get_object_or_404(
        AnnouncementAttachment.objects.select_related('announcement', 'announcement__course'),
        pk=pk
    )
    announcement = attachment.announcement
    course = announcement.course

    if request.method != 'POST':
        return redirect('courses:course_detail', pk=course.pk)

    if not (is_admin(request.user) or CourseInstructor.objects.filter(course=course, instructor=request.user).exists()):
        messages.error(request, 'You are not authorized to delete this announcement attachment.')
        return redirect('courses:course_detail', pk=course.pk)

    if attachment.file:
        attachment.file.delete(save=False)

    attachment.delete()

    messages.success(request, 'Announcement attachment deleted successfully.')
    return redirect('courses:course_detail', pk=course.pk)