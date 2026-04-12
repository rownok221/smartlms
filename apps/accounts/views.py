from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

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

    context = {
        'page_title': 'Admin Dashboard',
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def instructor_dashboard(request):
    if not is_instructor(request.user):
        messages.error(request, 'You are not authorized to access the instructor dashboard.')
        return redirect('accounts:dashboard_redirect')

    context = {
        'page_title': 'Instructor Dashboard',
    }
    return render(request, 'accounts/instructor_dashboard.html', context)


@login_required
def student_dashboard(request):
    if not is_student(request.user) and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to access the student dashboard.')
        return redirect('accounts:dashboard_redirect')

    context = {
        'page_title': 'Student Dashboard',
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')

    return redirect('accounts:dashboard_redirect')