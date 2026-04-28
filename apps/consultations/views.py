from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.courses.models import Course, CourseInstructor, Enrollment

from .forms import ConsultationRequestForm, ConsultationResponseForm
from .models import ConsultationRequest


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
def consultation_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view consultations for this course.')
        return redirect('courses:course_list')

    if can_manage_course(request.user, course):
        consultations = ConsultationRequest.objects.filter(
            course=course
        ).select_related('student', 'handled_by')
    else:
        consultations = ConsultationRequest.objects.filter(
            course=course,
            student=request.user
        ).select_related('student', 'handled_by')

    context = {
        'course': course,
        'consultations': consultations,
        'can_manage_consultations': can_manage_course(request.user, course),
        'can_request_consultation': is_student(request.user),
    }
    return render(request, 'consultations/consultation_list.html', context)


@login_required
def consultation_request_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not is_student(request.user):
        messages.error(request, 'Only students can request consultations.')
        return redirect('consultations:consultation_list', course_pk=course.pk)

    if not Enrollment.objects.filter(course=course, student=request.user).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = ConsultationRequestForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.course = course
            consultation.student = request.user
            consultation.save()

            messages.success(request, 'Consultation request submitted successfully.')
            return redirect('consultations:consultation_list', course_pk=course.pk)
    else:
        form = ConsultationRequestForm()

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'consultations/consultation_request_form.html', context)


@login_required
def consultation_respond(request, pk):
    consultation = get_object_or_404(
        ConsultationRequest.objects.select_related('course', 'student', 'handled_by'),
        pk=pk
    )
    course = consultation.course

    if not can_manage_course(request.user, course):
        messages.error(request, 'You are not authorized to respond to this consultation request.')
        return redirect('consultations:consultation_list', course_pk=course.pk)

    if request.method == 'POST':
        form = ConsultationResponseForm(request.POST, instance=consultation)
        if form.is_valid():
            updated_consultation = form.save(commit=False)

            scheduled_datetime = updated_consultation.scheduled_datetime
            status = updated_consultation.status

            if status in [
                ConsultationRequest.Status.ACCEPTED,
                ConsultationRequest.Status.RESCHEDULED,
            ] and scheduled_datetime:
                conflict_start = scheduled_datetime - timedelta(minutes=30)
                conflict_end = scheduled_datetime + timedelta(minutes=30)

                has_conflict = ConsultationRequest.objects.filter(
                    handled_by=request.user,
                    scheduled_datetime__gte=conflict_start,
                    scheduled_datetime__lte=conflict_end,
                    status__in=[
                        ConsultationRequest.Status.ACCEPTED,
                        ConsultationRequest.Status.RESCHEDULED,
                    ],
                ).exclude(pk=consultation.pk).exists()

                if has_conflict:
                    messages.error(
                        request,
                        'Scheduling conflict detected. You already have another consultation around this time.'
                    )
                    return render(
                        request,
                        'consultations/consultation_response_form.html',
                        {
                            'course': course,
                            'consultation': consultation,
                            'form': form,
                        }
                    )

            updated_consultation.handled_by = request.user
            updated_consultation.save()

            messages.success(request, 'Consultation request updated successfully.')
            return redirect('consultations:consultation_list', course_pk=course.pk)
    else:
        form = ConsultationResponseForm(instance=consultation)

    context = {
        'course': course,
        'consultation': consultation,
        'form': form,
    }
    return render(request, 'consultations/consultation_response_form.html', context)