import os

from django import forms


MAX_ATTACHMENT_SIZE_MB = 20
MAX_ATTACHMENT_SIZE_BYTES = MAX_ATTACHMENT_SIZE_MB * 1024 * 1024

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".txt",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
}


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            MultipleFileInput(attrs={
                "class": "form-control",
                "multiple": True,
            })
        )
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            if self.required:
                raise forms.ValidationError("Please select at least one file.")
            return []

        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            files = [single_file_clean(file, initial) for file in data]
        else:
            files = [single_file_clean(data, initial)]

        for file in files:
            validate_attachment_file(file)

        return files


def validate_attachment_file(file):
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_ATTACHMENT_EXTENSIONS))
        raise forms.ValidationError(
            f"Unsupported file type '{ext}'. Allowed file types: {allowed}"
        )

    if file.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise forms.ValidationError(
            f"File size cannot exceed {MAX_ATTACHMENT_SIZE_MB} MB."
        )