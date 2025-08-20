# hydroML/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home and core routes
    path('', core_views.home, name='home'),
    path('', include('core.urls')),
    
    # Application routes
    path('projects/', include('projects.urls')),
    path('tools/', include('data_tools.urls')),
    path('experiments/', include('experiments.urls')),
    path('connectors/', include('connectors.urls')),
    
    # Authentication routes
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)