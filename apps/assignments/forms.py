from django import forms

from .models import Assignment, Grade, Submission


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


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['marks_obtained', 'feedback']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter obtained marks',
                'min': 0,
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write feedback for the student',
                'rows': 5,
            }),
        }

    def __init__(self, *args, max_marks=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_marks = max_marks

    def clean_marks_obtained(self):
        marks = self.cleaned_data['marks_obtained']

        if marks < 0:
            raise forms.ValidationError("Marks cannot be negative.")

        if self.max_marks is not None and marks > self.max_marks:
            raise forms.ValidationError(
                f"Marks cannot exceed the assignment maximum of {self.max_marks}."
            )

        return marks