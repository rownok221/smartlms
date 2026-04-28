from django.urls import path

from .views import (
    consultation_list,
    consultation_request_create,
    consultation_respond,
)

app_name = 'consultations'

urlpatterns = [
    path('course/<int:course_pk>/', consultation_list, name='consultation_list'),
    path('course/<int:course_pk>/request/', consultation_request_create, name='consultation_request_create'),
    path('<int:pk>/respond/', consultation_respond, name='consultation_respond'),
]