from django.urls import path
from . import views, api


app_name = 'core'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Help/FAQ page
    path('help/', views.help_page, name='help'),
    
    # Hyperparameter Presets
    path('presets/', views.preset_list, name='preset_list'),
    path('presets/create/', views.preset_create, name='preset_create'),
    path('presets/<int:preset_id>/', views.preset_detail, name='preset_detail'),
    path('presets/<int:preset_id>/edit/', views.preset_update, name='preset_update'),
    path('presets/<int:preset_id>/delete/', views.preset_delete, name='preset_delete'),
    
    # API endpoints
    path('api/presets/', views.preset_api_list, name='preset_api_list'),
    path('api/presets/<int:preset_id>/', views.preset_api_detail, name='preset_api_detail'),
    
    # API endpoints for breadcrumb navigation
    path('api/projects/other/', api.get_other_projects, name='api_other_projects'),
    
    # API endpoints for notifications (commented out until Notification model is implemented)
    # path('api/notifications/', views.NotificationAPIView.as_view(), name='notifications_api'),
    # path('api/notifications/count/', views.get_unread_count, name='notifications_count'),
]