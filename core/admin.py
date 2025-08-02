# En core/admin.py
from django.contrib import admin
from .models import Project, Dataset

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'uploaded_file', 'created_at')
    list_filter = ('project',)
    search_fields = ('name', 'project__name')