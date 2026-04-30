from django import forms

from apps.accounts.models import User
from .models import CourseMentor, MentorshipRequest


class CourseMentorForm(forms.ModelForm):
    class Meta:
        model = CourseMentor
        fields = ['student', 'expertise', 'bio', 'is_active']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
            }),
            'expertise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Django basics, ERD, assignment help',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Short note about why this student can mentor others',
                'rows': 4,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)

        if course is not None:
            self.fields['student'].queryset = User.objects.filter(
                role=User.Role.STUDENT,
                course_enrollments__course=course
            ).exclude(
                mentor_assignments__course=course
            ).distinct()
        else:
            self.fields['student'].queryset = User.objects.none()


class MentorshipRequestForm(forms.ModelForm):
    preferred_datetime = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        })
    )

    class Meta:
        model = MentorshipRequest
        fields = ['topic', 'description', 'preferred_datetime']
        widgets = {
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Need help understanding Django views',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Briefly explain what you want help with',
                'rows': 5,
            }),
        }


class MentorshipResponseForm(forms.ModelForm):
    scheduled_datetime = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        })
    )

    class Meta:
        model = MentorshipRequest
        fields = ['status', 'scheduled_datetime', 'mentor_note']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'mentor_note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a short note for the student',
                'rows': 5,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].choices = [
            (MentorshipRequest.Status.ACCEPTED, "Accepted"),
            (MentorshipRequest.Status.RESCHEDULED, "Rescheduled"),
            (MentorshipRequest.Status.REJECTED, "Rejected"),
            (MentorshipRequest.Status.COMPLETED, "Completed"),
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        scheduled_datetime = cleaned_data.get('scheduled_datetime')

        if status in [
            MentorshipRequest.Status.ACCEPTED,
            MentorshipRequest.Status.RESCHEDULED,
        ] and not scheduled_datetime:
            raise forms.ValidationError(
                "A scheduled date and time is required when accepting or rescheduling a mentoring request."
            )

        return cleaned_data