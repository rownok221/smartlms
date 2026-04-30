from django.conf import settings
from django.db import models

from apps.courses.models import Course


class CourseMentor(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_mentors'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_assignments'
    )
    expertise = models.CharField(
        max_length=180,
        help_text="Example: Python basics, ER diagrams, Django setup"
    )
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_mentors'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')
        ordering = ['course__code', 'student__username']

    def __str__(self):
        return f"{self.student.username} - Mentor for {self.course.code}"


class MentorshipRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='mentorship_requests'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_mentorship_requests'
    )
    mentor = models.ForeignKey(
        CourseMentor,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )

    topic = models.CharField(max_length=180)
    description = models.TextField()
    preferred_datetime = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    mentor_note = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_mentorship_requests'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.requester.username} -> {self.mentor.student.username}"