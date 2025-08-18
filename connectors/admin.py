from django.contrib import admin
from .models import DatabaseConnection


@admin.register(DatabaseConnection)
class DatabaseConnectionAdmin(admin.ModelAdmin):
    """
    Optimized admin configuration for DatabaseConnection model.
    """
    list_display = ('name', 'database_type', 'host', 'port', 'user', 'created_at', 'is_active')
    list_filter = ('database_type', 'created_at', 'updated_at')
    search_fields = ('name', 'host', 'database_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'user')
        }),
        ('Connection Details', {
            'fields': ('database_type', 'host', 'port', 'database_name', 'username')
        }),
        ('Security', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active(self, obj):
        """Display if connection is recently used (within 30 days)."""
        from django.utils import timezone
        from datetime import timedelta
        recent_threshold = timezone.now() - timedelta(days=30)
        return obj.updated_at > recent_threshold
    is_active.boolean = True
    is_active.short_description = 'Recently Active'
