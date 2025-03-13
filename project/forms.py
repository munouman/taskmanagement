
from django.forms import DateInput

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
import mimetypes
from .models import Profile, Task, Category, Tag, Comment, Attachment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            # Get the MIME type using mimetypes
            content_type, encoding = mimetypes.guess_type(file.name)

            # Define allowed MIME types
            valid_file_types = ['image/jpeg', 'image/png', 'application/pdf']

            # Validate the file type
            if content_type not in valid_file_types:
                raise forms.ValidationError("Only JPG, PNG, and PDF files are allowed.")

        return file


class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Assign To"
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Tags"
    )

    new_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Add custom tags (comma separated)', 'class': 'form-control'}),
        label="New Tags"
    )

    due_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label="Due Date"
    )

    priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    status = forms.ChoiceField(
        choices=Task.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Allow tasks to be created without a category
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'assigned_to', 'category', 'tags']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date < date.today():
            raise ValidationError("Due date cannot be in the past.")
        return due_date

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            self.save_m2m()  # Ensures Many-to-Many relations are handled properly

        # Add new tags if entered
        new_tag_names = self.cleaned_data.get('new_tags', '')
        if new_tag_names:
            tag_names = [name.strip() for name in new_tag_names.split(',') if name.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                task.tags.add(tag)

        return task


class ProfileForm(forms.ModelForm):
    display_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your display name'})
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    class Meta:
        model = Profile
        fields = ['display_name', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ != 'ClearableFileInput':  # Avoid overriding file input styling
                field.widget.attrs.update({'class': 'form-control'})
