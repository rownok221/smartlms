from django import forms

from apps.core.form_fields import MultipleFileField

from .models import Announcement, Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course title',
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course code',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course description',
                'rows': 5,
            }),
        }


class AnnouncementForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        help_text="Optional: attach lecture slides, study materials, practice questions, or PDFs."
    )

    class Meta:
        model = Announcement
        fields = ['title', 'message', 'is_pinned', 'attachments']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter announcement title',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write the announcement message',
                'rows': 6,
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class AnnouncementAttachmentForm(forms.Form):
    attachments = MultipleFileField(
        required=True,
        help_text="Attach lecture slides, study materials, practice questions, PDFs, or ZIP files."
    )