from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.courses.models import Course


def submission_upload_path(instance, filename):
    return (
        f"submissions/course_{instance.assignment.course.id}/"
        f"assignment_{instance.assignment.id}/"
        f"student_{instance.student.id}/{filename}"
    )


class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assignments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', 'title']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    @property
    def is_past_deadline(self):
        return timezone.now() > self.deadline


class Submission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        LATE = "LATE", "Late"

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    file = models.FileField(upload_to=submission_upload_path)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-last_updated_at']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class Grade(models.Model):
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='grade'
    )
    marks_obtained = models.PositiveIntegerField()
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-graded_at']

    def __str__(self):
        return f"Grade for {self.submission.student.username} - {self.submission.assignment.title}"