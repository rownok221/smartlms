from django.urls import path

from .views import (
    UserLoginView,
    admin_dashboard,
    dashboard_redirect,
    instructor_dashboard,
    password_reset_info,
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

    path('password-reset/', password_reset_info, name='password_reset'),
]