from django.urls import path

from .views import announcement_create, course_create, course_detail, course_list

app_name = 'courses'

urlpatterns = [
    path('', course_list, name='course_list'),
    path('create/', course_create, name='course_create'),
    path('<int:course_pk>/announcements/create/', announcement_create, name='announcement_create'),
    path('<int:pk>/', course_detail, name='course_detail'),
]