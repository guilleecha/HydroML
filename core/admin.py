from django.contrib import admin
from .models import HyperparameterPreset


@admin.register(HyperparameterPreset)
class HyperparameterPresetAdmin(admin.ModelAdmin):
    """
    Optimized admin configuration for HyperparameterPreset model.
    """
    list_display = ('name', 'model_type', 'user', 'created_at')
    list_filter = ('model_type', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'user')
        }),
        ('Configuration', {
            'fields': ('model_type', 'hyperparameters')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
