from django.urls import path

from .views import (
    thread_create,
    thread_detail,
    thread_list,
    toggle_thread_lock,
    toggle_thread_pin,
)

app_name = 'discussions'

urlpatterns = [
    path('course/<int:course_pk>/', thread_list, name='thread_list'),
    path('course/<int:course_pk>/create/', thread_create, name='thread_create'),
    path('<int:pk>/', thread_detail, name='thread_detail'),
    path('<int:pk>/toggle-pin/', toggle_thread_pin, name='toggle_thread_pin'),
    path('<int:pk>/toggle-lock/', toggle_thread_lock, name='toggle_thread_lock'),
]