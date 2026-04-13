from django import forms

from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        })
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline', 'max_marks']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter assignment title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter assignment description',
                'rows': 5,
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter maximum marks',
                'min': 1,
            }),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }