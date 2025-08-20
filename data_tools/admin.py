from django.contrib import admin
from .models import ProcessingTask, ExportJob, ExportTemplate


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


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExportJob model.
    """
    list_display = (
        'id', 'user', 'datasource_name', 'format', 'status', 
        'progress', 'file_size_display', 'created_at', 'is_expired'
    )
    list_filter = ('status', 'format', 'created_at', 'expires_at')
    search_fields = ('id', 'user__username', 'datasource__name', 'file_path')
    readonly_fields = ('id', 'created_at', 'started_at', 'completed_at', 'duration_display')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'datasource', 'format', 'status', 'progress')
        }),
        ('Configuration', {
            'fields': ('filters',),
            'classes': ('collapse',)
        }),
        ('File Information', {
            'fields': ('file_path', 'file_size', 'row_count'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at', 'expires_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    def datasource_name(self, obj):
        """Display datasource name."""
        return obj.datasource.name
    datasource_name.short_description = 'DataSource'
    
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        if not obj.file_size:
            return "N/A"
        
        # Convert bytes to human readable format
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'File Size'
    
    def duration_display(self, obj):
        """Display job duration."""
        duration = obj.duration_seconds
        if duration is None:
            return "N/A"
        
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{duration:.2f}s"
    duration_display.short_description = 'Duration'
    
    def is_expired(self, obj):
        """Display if export is expired."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExportTemplate model.
    """
    list_display = (
        'name', 'user', 'template_type', 'format_display', 
        'usage_count', 'is_active', 'created_at', 'last_used_at'
    )
    list_filter = ('template_type', 'is_active', 'created_at', 'last_used_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('usage_count', 'created_at', 'updated_at', 'last_used_at')
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user', 'template_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('configuration',),
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def format_display(self, obj):
        """Display export format from configuration."""
        return obj.format.upper()
    format_display.short_description = 'Format'