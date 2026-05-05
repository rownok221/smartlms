from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.courses.models import Course, CourseInstructor, Enrollment

from .forms import ConsultationRequestForm, ConsultationResponseForm
from .models import ConsultationRequest


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


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


@login_required
def consultation_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view consultation requests for this course.')
        return redirect('courses:course_list')

    can_manage_consultations = is_admin(request.user) or is_instructor_for_course(request.user, course)
    can_request_consultation = is_enrolled_student(request.user, course)

    if can_manage_consultations:
        consultation_requests = ConsultationRequest.objects.filter(
            course=course
        ).select_related('student').order_by('-created_at')
    else:
        consultation_requests = ConsultationRequest.objects.filter(
            course=course,
            student=request.user
        ).select_related('student').order_by('-created_at')

    context = {
        'course': course,
        'consultation_requests': consultation_requests,
        'can_manage_consultations': can_manage_consultations,
        'can_request_consultation': can_request_consultation,
    }
    return render(request, 'consultations/consultation_list.html', context)


@login_required
def consultation_request_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not is_enrolled_student(request.user, course):
        messages.error(request, 'Only enrolled students can request consultations for this course.')
        return redirect('consultations:consultation_list', course_pk=course.pk)

    if request.method == 'POST':
        form = ConsultationRequestForm(request.POST)

        if form.is_valid():
            consultation_request = form.save(commit=False)
            consultation_request.course = course
            consultation_request.student = request.user
            consultation_request.status = ConsultationRequest.Status.PENDING
            consultation_request.save()

            messages.success(request, 'Consultation request submitted successfully.')
            return redirect('consultations:consultation_list', course_pk=course.pk)

        messages.error(request, 'Please correct the errors below and submit again.')
    else:
        form = ConsultationRequestForm()

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'consultations/consultation_request_form.html', context)


@login_required
def consultation_respond(request, pk):
    consultation_request = get_object_or_404(
        ConsultationRequest.objects.select_related('course', 'student'),
        pk=pk
    )
    course = consultation_request.course

    if not (is_admin(request.user) or is_instructor_for_course(request.user, course)):
        messages.error(request, 'You are not authorized to respond to this consultation request.')
        return redirect('consultations:consultation_list', course_pk=course.pk)

    if request.method == 'POST':
        form = ConsultationResponseForm(request.POST, instance=consultation_request)

        if form.is_valid():
            form.save()
            messages.success(request, 'Consultation request updated successfully.')
            return redirect('consultations:consultation_list', course_pk=course.pk)

        messages.error(request, 'Please correct the errors below and submit again.')
    else:
        form = ConsultationResponseForm(instance=consultation_request)

    context = {
        'course': course,
        'consultation_request': consultation_request,
        'form': form,
    }
    return render(request, 'consultations/consultation_response_form.html', context)