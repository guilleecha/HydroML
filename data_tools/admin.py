from django.contrib import admin
from .models import ProcessingTask


@admin.register(ProcessingTask)
class ProcessingTaskAdmin(admin.ModelAdmin):
    """
    Optimized admin configuration for ProcessingTask model.
    """
    list_display = ('id', 'task_type', 'status', 'created_at', 'duration', 'has_errors')
    list_filter = ('status', 'task_type', 'created_at')
    search_fields = ('id', 'task_data', 'error_message')
    readonly_fields = ('created_at', 'duration')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('task_type', 'status')
        }),
        ('Task Data', {
            'fields': ('task_data', 'result'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'duration'),
            'classes': ('collapse',)
        }),
    )
    
    def duration(self, obj):
        """Calculate and display task duration."""
        if obj.created_at:
            from django.utils import timezone
            # Si la tarea no tiene un campo updated_at, calculamos desde la creación hasta ahora
            # o usamos algún otro campo si existe un tiempo de finalización
            end_time = timezone.now()  # Por defecto usamos el tiempo actual
            delta = end_time - obj.created_at
            return f"{delta.total_seconds():.2f}s"
        return "N/A"
    duration.short_description = 'Duration'
    
    def has_errors(self, obj):
        """Display if task has error messages."""
        return bool(obj.error_message)
    has_errors.boolean = True
    has_errors.short_description = 'Has Errors'