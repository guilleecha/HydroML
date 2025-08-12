# data_tools/urls.py
from django.urls import path
from .views import visualization_views, preparation_views

app_name = 'data_tools'

urlpatterns = [
    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('viewer/<uuid:pk>/',
         visualization_views.data_viewer_page,
         name='data_viewer_page'),

    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('api/get_data/<uuid:pk>/',
         visualization_views.get_datasource_json,
         name='get_datasource_json'),

    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('preparer/<uuid:pk>/',
         preparation_views.data_preparer_page,
         name='data_preparer_page'),
]