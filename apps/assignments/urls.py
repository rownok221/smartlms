from django.urls import path

from .views import (
    assignment_attachment_delete,
    assignment_create,
    assignment_detail,
    assignment_list,
    assignment_update,
    grade_submission,
    submit_assignment,
)

app_name = 'assignments'

urlpatterns = [
    path('course/<int:course_pk>/', assignment_list, name='assignment_list'),
    path('course/<int:course_pk>/create/', assignment_create, name='assignment_create'),
    path('<int:pk>/', assignment_detail, name='assignment_detail'),
    path('<int:pk>/edit/', assignment_update, name='assignment_update'),
    path('<int:pk>/submit/', submit_assignment, name='submit_assignment'),
    path('attachment/<int:pk>/delete/', assignment_attachment_delete, name='assignment_attachment_delete'),
    path('submission/<int:submission_pk>/grade/', grade_submission, name='grade_submission'),
]