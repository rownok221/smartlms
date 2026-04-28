from django.conf import settings
from django.db import models

from apps.courses.models import Course


class ConsultationRequest(models.Model):
    class Mode(models.TextChoices):
        IN_PERSON = "IN_PERSON", "In Person"
        ONLINE = "ONLINE", "Online"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='consultation_requests'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultation_requests'
    )
    topic = models.CharField(max_length=180)
    description = models.TextField()
    preferred_datetime = models.DateTimeField()
    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.IN_PERSON
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    instructor_note = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_consultations'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.student.username} - {self.topic}"