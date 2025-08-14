from django.urls import path
from . import views

app_name = 'connectors'

urlpatterns = [
    path('', views.database_connection_list, name='database_connection_list'),
    path('create/', views.database_connection_create, name='database_connection_create'),
    path('<int:pk>/delete/', views.database_connection_delete, name='database_connection_delete'),
]