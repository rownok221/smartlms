from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.courses.models import Course, CourseInstructor, Enrollment

from .forms import CourseMentorForm, MentorshipRequestForm, MentorshipResponseForm
from .models import CourseMentor, MentorshipRequest


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def is_instructor(user):
    return user.role == User.Role.INSTRUCTOR


def is_student(user):
    return user.role == User.Role.STUDENT


def can_access_course(user, course):
    if is_admin(user):
        return True
    if is_instructor(user):
        return CourseInstructor.objects.filter(course=course, instructor=user).exists()
    if is_student(user):
        return Enrollment.objects.filter(course=course, student=user).exists()
    return False


def can_manage_course(user, course):
    if is_admin(user):
        return True
    if is_instructor(user):
        return CourseInstructor.objects.filter(course=course, instructor=user).exists()
    return False


@login_required
def mentor_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view mentorship for this course.')
        return redirect('courses:course_list')

    mentors = CourseMentor.objects.filter(
        course=course,
        is_active=True
    ).select_related('student', 'approved_by')

    is_current_user_mentor = CourseMentor.objects.filter(
        course=course,
        student=request.user,
        is_active=True
    ).exists()

    if can_manage_course(request.user, course):
        mentorship_requests = MentorshipRequest.objects.filter(
            course=course
        ).select_related('requester', 'mentor__student', 'handled_by')
    elif is_current_user_mentor:
        mentorship_requests = MentorshipRequest.objects.filter(
            Q(requester=request.user) | Q(mentor__student=request.user),
            course=course
        ).select_related('requester', 'mentor__student', 'handled_by')
    else:
        mentorship_requests = MentorshipRequest.objects.filter(
            course=course,
            requester=request.user
        ).select_related('requester', 'mentor__student', 'handled_by')

    context = {
        'course': course,
        'mentors': mentors,
        'mentorship_requests': mentorship_requests,
        'can_manage_mentorship': can_manage_course(request.user, course),
        'can_request_mentorship': is_student(request.user),
        'is_current_user_mentor': is_current_user_mentor,
    }
    return render(request, 'mentorship/mentor_list.html', context)


@login_required
def mentor_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_manage_course(request.user, course):
        messages.error(request, 'You are not authorized to assign peer mentors for this course.')
        return redirect('mentorship:mentor_list', course_pk=course.pk)

    if request.method == 'POST':
        form = CourseMentorForm(request.POST, course=course)
        if form.is_valid():
            mentor = form.save(commit=False)
            mentor.course = course
            mentor.approved_by = request.user
            mentor.save()

            messages.success(request, 'Peer mentor assigned successfully.')
            return redirect('mentorship:mentor_list', course_pk=course.pk)
    else:
        form = CourseMentorForm(course=course)

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'mentorship/mentor_form.html', context)


@login_required
def mentorship_request_create(request, mentor_pk):
    mentor = get_object_or_404(
        CourseMentor.objects.select_related('course', 'student'),
        pk=mentor_pk,
        is_active=True
    )
    course = mentor.course

    if not is_student(request.user):
        messages.error(request, 'Only students can request peer mentoring.')
        return redirect('mentorship:mentor_list', course_pk=course.pk)

    if not Enrollment.objects.filter(course=course, student=request.user).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:course_list')

    if mentor.student == request.user:
        messages.error(request, 'You cannot request mentoring from yourself.')
        return redirect('mentorship:mentor_list', course_pk=course.pk)

    if request.method == 'POST':
        form = MentorshipRequestForm(request.POST)
        if form.is_valid():
            mentorship_request = form.save(commit=False)
            mentorship_request.course = course
            mentorship_request.requester = request.user
            mentorship_request.mentor = mentor
            mentorship_request.save()

            messages.success(request, 'Mentorship request submitted successfully.')
            return redirect('mentorship:mentor_list', course_pk=course.pk)
    else:
        form = MentorshipRequestForm()

    context = {
        'course': course,
        'mentor': mentor,
        'form': form,
    }
    return render(request, 'mentorship/mentorship_request_form.html', context)


@login_required
def mentorship_respond(request, pk):
    mentorship_request = get_object_or_404(
        MentorshipRequest.objects.select_related(
            'course',
            'requester',
            'mentor',
            'mentor__student',
            'handled_by'
        ),
        pk=pk
    )
    course = mentorship_request.course

    is_assigned_mentor = mentorship_request.mentor.student == request.user

    if not (can_manage_course(request.user, course) or is_assigned_mentor):
        messages.error(request, 'You are not authorized to respond to this mentoring request.')
        return redirect('mentorship:mentor_list', course_pk=course.pk)

    if request.method == 'POST':
        form = MentorshipResponseForm(request.POST, instance=mentorship_request)
        if form.is_valid():
            updated_request = form.save(commit=False)

            scheduled_datetime = updated_request.scheduled_datetime
            status = updated_request.status

            if status in [
                MentorshipRequest.Status.ACCEPTED,
                MentorshipRequest.Status.RESCHEDULED,
            ] and scheduled_datetime:
                conflict_start = scheduled_datetime - timedelta(minutes=30)
                conflict_end = scheduled_datetime + timedelta(minutes=30)

                has_conflict = MentorshipRequest.objects.filter(
                    mentor=mentorship_request.mentor,
                    scheduled_datetime__gte=conflict_start,
                    scheduled_datetime__lte=conflict_end,
                    status__in=[
                        MentorshipRequest.Status.ACCEPTED,
                        MentorshipRequest.Status.RESCHEDULED,
                    ],
                ).exclude(pk=mentorship_request.pk).exists()

                if has_conflict:
                    messages.error(
                        request,
                        'Scheduling conflict detected. This mentor already has another mentoring session around this time.'
                    )
                    return render(
                        request,
                        'mentorship/mentorship_response_form.html',
                        {
                            'course': course,
                            'mentorship_request': mentorship_request,
                            'form': form,
                        }
                    )

            updated_request.handled_by = request.user
            updated_request.save()

            messages.success(request, 'Mentorship request updated successfully.')
            return redirect('mentorship:mentor_list', course_pk=course.pk)
    else:
        form = MentorshipResponseForm(instance=mentorship_request)

    context = {
        'course': course,
        'mentorship_request': mentorship_request,
        'form': form,
    }
    return render(request, 'mentorship/mentorship_response_form.html', context)