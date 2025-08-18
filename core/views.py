"""
Core views module - refactored to use class-based views.

This module has been restructured to use Django's generic class-based views
for better maintainability and code reuse. All views have been moved to
specialized modules within the core/views/ package.

Legacy function-based views are preserved for backward compatibility.
"""

# Import all views from specialized modules
from .views.dashboard_views import (
    home,
    DashboardView,
    HelpPageView,
    # Legacy function-based views
    dashboard_view,
    help_page,
)

from .views.preset_views import (
    PresetListView,
    PresetDetailView, 
    PresetCreateView,
    PresetUpdateView,
    PresetDeleteView,
    PresetAPIListView,
    PresetAPIDetailView,
    # Legacy function-based views
    preset_list,
    preset_detail,
    preset_create,
    preset_update,
    preset_delete,
    preset_api_list,
    preset_api_detail,
)

# Note: Notification views are commented out until the Notification model is implemented
# These can be added to a notification_views.py module when needed