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


def is_instructor_for_course(user, course):
    return CourseInstructor.objects.filter(
        course=course,
        instructor=user
    ).exists()


def is_enrolled_student(user, course):
    return Enrollment.objects.filter(
        course=course,
        student=user
    ).exists()


def can_access_course(user, course):
    return (
        is_admin(user)
        or is_instructor_for_course(user, course)
        or is_enrolled_student(user, course)
    )


def can_manage_course(user, course):
    return is_admin(user) or is_instructor_for_course(user, course)


def find_mentorship_schedule_conflict(mentorship_request, scheduled_datetime):
    """
    Blocks scheduling if the same peer mentor already has an accepted/rescheduled
    mentoring session within ±1 hour of the selected time.
    """
    conflict_start = scheduled_datetime - timedelta(hours=1)
    conflict_end = scheduled_datetime + timedelta(hours=1)

    return MentorshipRequest.objects.filter(
        mentor=mentorship_request.mentor,
        status__in=[
            MentorshipRequest.Status.ACCEPTED,
            MentorshipRequest.Status.RESCHEDULED,
        ],
        scheduled_datetime__isnull=False,
        scheduled_datetime__gte=conflict_start,
        scheduled_datetime__lte=conflict_end,
    ).exclude(
        pk=mentorship_request.pk
    ).select_related(
        'requester',
        'mentor',
        'mentor__student',
    ).first()


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

        messages.error(request, 'Please correct the errors below and submit again.')
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

    if not is_enrolled_student(request.user, course):
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
            mentorship_request.status = MentorshipRequest.Status.PENDING
            mentorship_request.save()

            messages.success(request, 'Mentorship request submitted successfully.')
            return redirect('mentorship:mentor_list', course_pk=course.pk)

        messages.error(request, 'Please correct the errors below and submit again.')
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
            'mentor',
            'mentor__course',
            'mentor__student',
            'requester',
        ),
        pk=pk
    )
    course = mentorship_request.course

    can_respond = (
        is_admin(request.user)
        or is_instructor_for_course(request.user, course)
        or mentorship_request.mentor.student == request.user
    )

    if not can_respond:
        messages.error(request, 'You are not authorized to respond to this mentorship request.')
        return redirect('mentorship:mentor_list', course_pk=course.pk)

    if request.method == 'POST':
        form = MentorshipResponseForm(request.POST, instance=mentorship_request)

        if form.is_valid():
            selected_status = form.cleaned_data.get('status')
            scheduled_datetime = form.cleaned_data.get('scheduled_datetime')

            schedule_required_statuses = [
                MentorshipRequest.Status.ACCEPTED,
                MentorshipRequest.Status.RESCHEDULED,
            ]

            if selected_status in schedule_required_statuses and not scheduled_datetime:
                form.add_error(
                    'scheduled_datetime',
                    'Scheduled date and time is required when accepting or rescheduling a mentorship request.'
                )
                messages.warning(
                    request,
                    'Please select a scheduled date and time before accepting or rescheduling this mentorship request.'
                )

            elif selected_status in schedule_required_statuses:
                conflict = find_mentorship_schedule_conflict(
                    mentorship_request=mentorship_request,
                    scheduled_datetime=scheduled_datetime
                )

                if conflict:
                    conflict_requester = conflict.requester.full_name or conflict.requester.username
                    conflict_time = conflict.scheduled_datetime.strftime('%b %d, %Y %I:%M %p')

                    form.add_error(
                        'scheduled_datetime',
                        (
                            f'Conflict detected. This mentor already has a session with '
                            f'{conflict_requester} at {conflict_time}. Keep at least a 1-hour gap.'
                        )
                    )

                    messages.warning(
                        request,
                        'Schedule conflict: this mentor already has another mentorship session within 1 hour of this time.'
                    )
                else:
                    mentorship = form.save(commit=False)
                    mentorship.handled_by = request.user
                    mentorship.save()

                    messages.success(request, 'Mentorship request updated successfully.')
                    return redirect('mentorship:mentor_list', course_pk=course.pk)

            else:
                mentorship = form.save(commit=False)
                mentorship.handled_by = request.user
                mentorship.save()

                messages.success(request, 'Mentorship request updated successfully.')
                return redirect('mentorship:mentor_list', course_pk=course.pk)

        else:
            messages.error(request, 'Please correct the errors below and submit again.')

    else:
        form = MentorshipResponseForm(instance=mentorship_request)

    context = {
        'course': course,
        'mentorship_request': mentorship_request,
        'form': form,
    }
    return render(request, 'mentorship/mentorship_response_form.html', context)