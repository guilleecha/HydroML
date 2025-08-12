from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')),  # URLs para la biblioteca
    path('tools/', include('data_tools.urls')),  # URLs para el taller
    path('experiments/', include('experiments.urls')),  # URLs para el laboratorio

    path('', core_views.home, name='home'),  # <-- ¡NUEVA! La raíz del sitio apunta aquí.

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)