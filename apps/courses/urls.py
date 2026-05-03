from django.urls import path

from .views import (
    announcement_attachment_add,
    announcement_attachment_delete,
    announcement_create,
    course_create,
    course_detail,
    course_list,
)

app_name = 'courses'

urlpatterns = [
    path('', course_list, name='course_list'),
    path('create/', course_create, name='course_create'),
    path('<int:course_pk>/announcements/create/', announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/attachments/add/', announcement_attachment_add, name='announcement_attachment_add'),
    path('announcement-attachments/<int:pk>/delete/', announcement_attachment_delete, name='announcement_attachment_delete'),
    path('<int:pk>/', course_detail, name='course_detail'),
]