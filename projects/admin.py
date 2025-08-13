from django.contrib import admin
from .models import Project, DataSource, FeatureSet

# Opcional: Clases para mejorar la visualización en el admin
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('created_at',)

class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'data_type', 'uploaded_at')
    search_fields = ('name', 'project__name')
    list_filter = ('data_type', 'project')

# Registramos los modelos
admin.site.register(Project, ProjectAdmin)
admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(FeatureSet)