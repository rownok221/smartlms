from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .views import (
    UserLoginView,
    admin_dashboard,
    dashboard_redirect,
    instructor_dashboard,
    student_dashboard,
    user_logout,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),

    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/instructor/', instructor_dashboard, name='instructor_dashboard'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]