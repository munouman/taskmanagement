from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import mimetypes

ROLE_CHOICES = [
    ('Manager', 'Manager'),
    ('Sub-Manager', 'Sub-Manager'),
    ('Officer', 'Officer'),
]
# Category Model with unique name
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Tag Model
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Task Model with validation for due date and other improvements
class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    assigned_to = models.ManyToManyField(User, blank=True, related_name='tasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

    # Validate that the due_date is not in the past
    def clean(self):
        if self.due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")

    # Ensure there's at least one user assigned to the task
    def save(self, *args, **kwargs):
        if not self.assigned_to.exists():
            raise ValidationError("At least one user must be assigned to the task.")
        super(Task, self).save(*args, **kwargs)


# Comment Model
class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"


# Attachment Model with file type validation
class Attachment(models.Model):
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, related_name='uploaded_attachments', on_delete=models.CASCADE)

    def __str__(self):
        return f"Attachment for {self.task.title} by {self.uploaded_by.username}"

    # Validate file type (only images and documents in this case)
    def clean(self):
        valid_file_types = ['image/jpeg', 'image/png', 'application/pdf']

        if self.file:
            content_type, encoding = mimetypes.guess_type(self.file.name)  # Guess type based on filename

        if content_type not in valid_file_types:
            raise ValidationError(f"Invalid file type: {content_type}. Allowed types: JPG, PNG, PDF.")
# Ensure that the file is not too large (example: 5MB max)
    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super(Attachment, self).save(*args, **kwargs)


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Officer')
    display_name = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


