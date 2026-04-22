from django.urls import path

from .views import (
    assignment_create,
    assignment_detail,
    assignment_list,
    grade_submission,
    submit_assignment,
)

app_name = 'assignments'

urlpatterns = [
    path('course/<int:course_pk>/', assignment_list, name='assignment_list'),
    path('course/<int:course_pk>/create/', assignment_create, name='assignment_create'),
    path('<int:pk>/', assignment_detail, name='assignment_detail'),
    path('<int:pk>/submit/', submit_assignment, name='submit_assignment'),
    path('submission/<int:submission_pk>/grade/', grade_submission, name='grade_submission'),
]