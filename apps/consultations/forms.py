from django import forms
from django.utils import timezone

from .models import ConsultationRequest


class ConsultationRequestForm(forms.ModelForm):
    preferred_datetime = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        })
    )

    class Meta:
        model = ConsultationRequest
        fields = ['topic', 'description', 'preferred_datetime']
        widgets = {
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Need help understanding assignment requirements',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Briefly explain what you need help with.',
            }),
        }


class ConsultationResponseForm(forms.ModelForm):
    scheduled_datetime = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        })
    )

    class Meta:
        model = ConsultationRequest
        fields = ['status', 'scheduled_datetime', 'instructor_note']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'instructor_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Add a response note for the student.',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.scheduled_datetime:
            scheduled = timezone.localtime(self.instance.scheduled_datetime)
            self.initial['scheduled_datetime'] = scheduled.strftime('%Y-%m-%dT%H:%M')