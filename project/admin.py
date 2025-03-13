from bs4 import Comment

from django.contrib import admin
from .models import Profile, Task, Category, Tag, Comment, Attachment

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'due_date', 'assigned_to')
    list_filter = ('status', 'priority', 'category', 'tags')

admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Attachment)
