from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.assignments.models import Assignment, Submission
from apps.consultations.models import ConsultationRequest
from apps.courses.models import Announcement, Course, CourseInstructor, Enrollment
from apps.mentorship.models import CourseMentor, MentorshipRequest

from .forms import CustomLoginForm
from .models import User


def home(request):
    return render(request, 'home.html')


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('accounts:dashboard_redirect')


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def is_instructor(user):
    return user.role == User.Role.INSTRUCTOR


def is_student(user):
    return user.role == User.Role.STUDENT


@login_required
def dashboard_redirect(request):
    if is_admin(request.user):
        return redirect('accounts:admin_dashboard')
    elif is_instructor(request.user):
        return redirect('accounts:instructor_dashboard')
    else:
        return redirect('accounts:student_dashboard')


@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'You are not authorized to access the admin dashboard.')
        return redirect('accounts:dashboard_redirect')

    recent_announcements = Announcement.objects.select_related('course', 'posted_by')[:5]
    recent_courses = Course.objects.select_related('created_by').order_by('-created_at')[:4]

    context = {
        'page_title': 'Admin Dashboard',
        'user_count': User.objects.count(),
        'course_count': Course.objects.count(),
        'assignment_count': Assignment.objects.count(),
        'submission_count': Submission.objects.count(),

        'consultation_count': ConsultationRequest.objects.count(),
        'pending_consultation_count': ConsultationRequest.objects.filter(
            status=ConsultationRequest.Status.PENDING
        ).count(),

        'mentor_count': CourseMentor.objects.filter(is_active=True).count(),
        'mentorship_request_count': MentorshipRequest.objects.count(),
        'pending_mentorship_count': MentorshipRequest.objects.filter(
            status=MentorshipRequest.Status.PENDING
        ).count(),

        'recent_announcements': recent_announcements,
        'recent_courses': recent_courses,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def instructor_dashboard(request):
    if not is_instructor(request.user):
        messages.error(request, 'You are not authorized to access the instructor dashboard.')
        return redirect('accounts:dashboard_redirect')

    assigned_courses = Course.objects.filter(
        course_instructors__instructor=request.user
    ).distinct()

    recent_announcements = Announcement.objects.filter(
        course__course_instructors__instructor=request.user
    ).select_related('course', 'posted_by').distinct()[:5]

    recent_submissions = Submission.objects.filter(
        assignment__course__course_instructors__instructor=request.user
    ).select_related('assignment', 'student').distinct().order_by('-submitted_at')[:5]

    context = {
        'page_title': 'Instructor Dashboard',
        'assigned_courses': assigned_courses[:4],
        'assigned_course_count': assigned_courses.count(),

        'assignment_count': Assignment.objects.filter(
            course__course_instructors__instructor=request.user
        ).distinct().count(),

        'submission_count': Submission.objects.filter(
            assignment__course__course_instructors__instructor=request.user
        ).distinct().count(),

        'consultation_count': ConsultationRequest.objects.filter(
            course__course_instructors__instructor=request.user
        ).distinct().count(),

        'pending_consultation_count': ConsultationRequest.objects.filter(
            course__course_instructors__instructor=request.user,
            status=ConsultationRequest.Status.PENDING
        ).distinct().count(),

        'mentor_count': CourseMentor.objects.filter(
            course__course_instructors__instructor=request.user,
            is_active=True
        ).distinct().count(),

        'mentorship_request_count': MentorshipRequest.objects.filter(
            course__course_instructors__instructor=request.user
        ).distinct().count(),

        'pending_mentorship_count': MentorshipRequest.objects.filter(
            course__course_instructors__instructor=request.user,
            status=MentorshipRequest.Status.PENDING
        ).distinct().count(),

        'recent_announcements': recent_announcements,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'accounts/instructor_dashboard.html', context)


@login_required
def student_dashboard(request):
    if not is_student(request.user) and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to access the student dashboard.')
        return redirect('accounts:dashboard_redirect')

    enrolled_courses = Course.objects.filter(
        enrollments__student=request.user
    ).distinct()

    recent_announcements = Announcement.objects.filter(
        course__enrollments__student=request.user
    ).select_related('course', 'posted_by').distinct()[:5]

    upcoming_assignments = Assignment.objects.filter(
        course__enrollments__student=request.user
    ).select_related('course').distinct().order_by('deadline')[:5]

    context = {
        'page_title': 'Student Dashboard',
        'enrolled_courses': enrolled_courses[:4],
        'upcoming_assignments': upcoming_assignments,

        'enrolled_course_count': enrolled_courses.count(),

        'assignment_count': Assignment.objects.filter(
            course__enrollments__student=request.user
        ).distinct().count(),

        'submission_count': Submission.objects.filter(
            student=request.user
        ).count(),

        'consultation_count': ConsultationRequest.objects.filter(
            student=request.user
        ).count(),

        'pending_consultation_count': ConsultationRequest.objects.filter(
            student=request.user,
            status=ConsultationRequest.Status.PENDING
        ).count(),

        'mentor_count': CourseMentor.objects.filter(
            student=request.user,
            is_active=True
        ).count(),

        'mentorship_request_count': MentorshipRequest.objects.filter(
            Q(requester=request.user) | Q(mentor__student=request.user)
        ).distinct().count(),

        'pending_mentorship_count': MentorshipRequest.objects.filter(
            Q(requester=request.user) | Q(mentor__student=request.user),
            status=MentorshipRequest.Status.PENDING
        ).distinct().count(),

        'recent_announcements': recent_announcements,
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')

    return redirect('accounts:dashboard_redirect')