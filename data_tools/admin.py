from django.contrib import admin
from .models import ProcessingTask

class ProcessingTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_type', 'status', 'created_at')
    list_filter = ('status', 'task_type')

admin.site.register(ProcessingTask, ProcessingTaskAdmin)