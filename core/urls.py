from django.urls import path
from . import views, api
from .views import dashboard_views, preset_views


app_name = 'core'

urlpatterns = [
    # Dashboard
    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),
    
    # Help/FAQ page
    path('help/', dashboard_views.HelpPageView.as_view(), name='help'),
    
    # Hyperparameter Presets
    path('presets/', preset_views.PresetListView.as_view(), name='preset_list'),
    path('presets/create/', preset_views.PresetCreateView.as_view(), name='preset_create'),
    path('presets/<int:pk>/', preset_views.PresetDetailView.as_view(), name='preset_detail'),
    path('presets/<int:pk>/edit/', preset_views.PresetUpdateView.as_view(), name='preset_update'),
    path('presets/<int:pk>/delete/', preset_views.PresetDeleteView.as_view(), name='preset_delete'),
    
    # API endpoints
    path('api/presets/', preset_views.PresetAPIListView.as_view(), name='preset_api_list'),
    path('api/presets/<int:pk>/', preset_views.PresetAPIDetailView.as_view(), name='preset_api_detail'),
    
    # API endpoints for breadcrumb navigation
    path('api/projects/other/', api.get_other_projects, name='api_other_projects'),
    
    # API endpoints for notifications (commented out until Notification model is implemented)
    # path('api/notifications/', views.NotificationAPIView.as_view(), name='notifications_api'),
    # path('api/notifications/count/', views.get_unread_count, name='notifications_count'),
]