from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task, Category, Tag, Comment, Attachment, Profile
from .forms import TaskForm, ProfileForm, CommentForm, AttachmentForm
from django.contrib.auth.forms import UserCreationForm


# Signal to create/update profile when a user is created
@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """Ensures a user profile is created and updated properly."""
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        instance.profile.save()


# User Registration View
def register(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully!")
            login(request, user)  # Log in the user
            return redirect('user_dashboard')  # Redirect to dashboard
    else:
        form = UserCreationForm()
    return render(request, 'project/register.html', {'form': form})


# Profile Update View
@login_required
def profile_update(request):
    """Handles profile update functionality."""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'project/profile_update.html', {'form': form})


# Profile View
@login_required
def profile_view(request):
    """Displays the user's profile."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'project/profile.html', {'profile': profile})


# Task List View with Filtering
@login_required
def task_list(request):
    """Displays the list of tasks with search and filter functionality."""
    tasks = Task.objects.select_related('category').prefetch_related('tags', 'assigned_to')

    # Filtering logic
    filters = Q()
    filter_params = {
        'status': request.GET.get('status'),
        'priority': request.GET.get('priority'),
        'category': request.GET.get('category'),
        'tag': request.GET.get('tag'),
        'due_date': request.GET.get('due_date'),
        'assigned_to': request.GET.get('assigned_to'),
        'search': request.GET.get('search'),
    }

    if filter_params['status']:
        filters &= Q(status=filter_params['status'])
    if filter_params['priority']:
        filters &= Q(priority=filter_params['priority'])
    if filter_params['category']:
        filters &= Q(category__name=filter_params['category'])
    if filter_params['tag']:
        filters &= Q(tags__name=filter_params['tag'])
    if filter_params['due_date']:
        filters &= Q(due_date=filter_params['due_date'])
    if filter_params['assigned_to']:
        filters &= Q(assigned_to__username=filter_params['assigned_to'])
    if filter_params['search']:
        filters &= Q(title__icontains=filter_params['search']) | Q(description__icontains=filter_params['search'])

    tasks = tasks.filter(filters).distinct()

    return render(request, 'project/task_list.html', {
        'tasks': tasks,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'users': User.objects.all(),
        **filter_params
    })


# Task Create View
@login_required
def task_create(request):
    """Handles task creation."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            task.assigned_to.set(form.cleaned_data['assigned_to'])  # Assign users
            messages.success(request, "Task created successfully!")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'project/task_form.html', {'form': form})


# Task Update View
@login_required
def task_update(request, task_id):
    """Handles task updates."""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            task.assigned_to.set(form.cleaned_data['assigned_to'])
            messages.success(request, "Task updated successfully!")
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'project/task_form.html', {'form': form})


# Task Delete View
@login_required
def task_delete(request, task_id):
    """Handles task deletion."""
    task = get_object_or_404(Task, id=task_id)

    if request.user == task.created_by or request.user.is_staff:
        if request.method == "POST":
            task.delete()
            messages.success(request, "Task deleted successfully.")
            return redirect('task_list')
    else:
        messages.error(request, "You do not have permission to delete this task.")
        return redirect('task_list')

    return render(request, 'project/task_confirm_delete.html', {'task': task})


# Task Detail View
@login_required
def task_detail(request, task_id):
    """Displays task details with comments and attachments."""
    task = get_object_or_404(Task.objects.prefetch_related('comments', 'attachments'), id=task_id)

    comment_form = CommentForm(request.POST or None)
    attachment_form = AttachmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")

        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, "Attachment uploaded successfully!")

        return redirect('task_detail', task_id=task.id)

    return render(request, 'project/task_detail.html', {
        'task': task,
        'comments': task.comments.all(),
        'attachments': task.attachments.all(),
        'comment_form': comment_form,
        'attachment_form': attachment_form,
    })


# User Dashboard View
@login_required
def user_dashboard(request):
    """Displays the dashboard with tasks assigned to the logged-in user."""
    tasks = Task.objects.filter(assigned_to=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status="Completed").count()
    overdue_tasks = tasks.filter(due_date__lt=timezone.now()).exclude(status='Completed').count()
    pending_tasks = tasks.filter(status="Pending").count()

    return render(request, 'project/user_dashboard.html', {
        "tasks": tasks,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "pending_tasks": pending_tasks,
    })
