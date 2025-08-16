from django.contrib import admin
from .models import MLExperiment, ExperimentSuite

@admin.register(MLExperiment)
class MLExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'model_name', 'status', 'suite', 'created_at')
    list_filter = ('status', 'model_name', 'project', 'suite')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'project')
        }),
        ('Data & Model Configuration', {
            'fields': ('input_datasource', 'target_column', 'model_name', 'feature_set', 'hyperparameters')
        }),
        ('Training Configuration', {
            'fields': ('test_split_size', 'split_random_state', 'split_strategy')
        }),
        ('Suite & Versioning', {
            'fields': ('suite', 'parent_experiment', 'forked_from', 'version')
        }),
        ('Results & Status', {
            'fields': ('status', 'results', 'artifact_paths')
        }),
        ('Publication', {
            'fields': ('is_public', 'published_at')
        }),
        ('External Integration', {
            'fields': ('mlflow_run_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ExperimentSuite)
class ExperimentSuiteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administrador para las Suites de Experimentos.
    """
    list_display = ('name', 'project', 'study_type', 'status', 'created_at')
    list_filter = ('study_type', 'status', 'project')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'started_at', 'completed_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'project')
        }),
        ('Study Configuration', {
            'fields': ('study_type', 'base_experiment', 'search_space', 'optimization_metric')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )