from django.contrib import admin
from .models import MLExperiment

class MLExperimentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'model_name', 'status', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'project__name')
    list_filter = ('status', 'model_name', 'project')

admin.site.register(MLExperiment, MLExperimentAdmin)