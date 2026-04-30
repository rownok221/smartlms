from django.urls import path

from .views import (
    mentor_create,
    mentor_list,
    mentorship_request_create,
    mentorship_respond,
)

app_name = 'mentorship'

urlpatterns = [
    path('course/<int:course_pk>/', mentor_list, name='mentor_list'),
    path('course/<int:course_pk>/assign/', mentor_create, name='mentor_create'),
    path('mentor/<int:mentor_pk>/request/', mentorship_request_create, name='mentorship_request_create'),
    path('request/<int:pk>/respond/', mentorship_respond, name='mentorship_respond'),
]