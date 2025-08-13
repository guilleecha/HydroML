# hydroML/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

    

urlpatterns = [
    path('admin/', admin.site.urls),

    # La raíz del sitio apunta a la vista 'home' de la app 'core'
    path('', core_views.home, name='home'),

    # La ruta '/projects/' carga el archivo urls.py de la app 'projects'
    path('projects/', include('projects.urls')),

    # La ruta '/tools/' carga el archivo urls.py de la app 'data_tools'
    path('tools/', include('data_tools.urls')),

    # La ruta '/experiments/' carga el archivo urls.py de la app 'experiments'
    path('experiments/', include('experiments.urls')),

    # La ruta '/accounts/' carga el archivo urls.py de la app 'accounts'
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)