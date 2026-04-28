from django.conf import settings
from django.db import models

from apps.courses.models import Course


class DiscussionThread(models.Model):
    class Category(models.TextChoices):
        GENERAL = "GENERAL", "General"
        ASSIGNMENT = "ASSIGNMENT", "Assignment"
        EXAM = "EXAM", "Exam"
        LECTURE = "LECTURE", "Lecture"

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='discussion_threads'
    )
    title = models.CharField(max_length=180)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_threads'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at', '-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class DiscussionReply(models.Model):
    thread = models.ForeignKey(
        DiscussionThread,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discussion_replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.created_by} on {self.thread.title}"