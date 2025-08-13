from django.contrib import admin
from .models import MLExperiment, ExperimentSuite

@admin.register(MLExperiment)
class MLExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'model_name', 'status', 'created_at')
    list_filter = ('status', 'model_name', 'project')
    search_fields = ('name', 'description')

@admin.register(ExperimentSuite)
class ExperimentSuiteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administrador para las Suites de Experimentos.
    """
    list_display = ('name', 'project', 'suite_type', 'status', 'created_at')
    list_filter = ('suite_type', 'status', 'project')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)