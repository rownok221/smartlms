from django import forms

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
        fields = ['topic', 'description', 'preferred_datetime', 'mode']
        widgets = {
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Need help understanding ER diagrams',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Briefly explain what you need help with',
                'rows': 5,
            }),
            'mode': forms.Select(attrs={
                'class': 'form-select',
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
                'placeholder': 'Write a note for the student',
                'rows': 5,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].choices = [
            (ConsultationRequest.Status.ACCEPTED, "Accepted"),
            (ConsultationRequest.Status.RESCHEDULED, "Rescheduled"),
            (ConsultationRequest.Status.REJECTED, "Rejected"),
            (ConsultationRequest.Status.COMPLETED, "Completed"),
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        scheduled_datetime = cleaned_data.get('scheduled_datetime')

        if status in [
            ConsultationRequest.Status.ACCEPTED,
            ConsultationRequest.Status.RESCHEDULED,
        ] and not scheduled_datetime:
            raise forms.ValidationError(
                "A scheduled date and time is required when accepting or rescheduling a consultation."
            )

        return cleaned_data