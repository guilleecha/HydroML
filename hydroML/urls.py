# hydroML/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # --- CAMBIOS AQUÍ ---
    path('', include('projects.urls')), # Apunta a la app de projects
    path('experiments/', include('experiments.urls')), # Y a la de experiments
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)