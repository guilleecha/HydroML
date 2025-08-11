from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')),  # URLs para la biblioteca
    path('tools/', include('data_tools.urls')),  # URLs para el taller
    path('experiments/', include('experiments.urls')),  # URLs para el laboratorio
]