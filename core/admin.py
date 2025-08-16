from django.contrib import admin
# from .models import Notification


# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     """
#     Django admin configuration for the Notification model.
#     """
#     list_display = ('user', 'message_preview', 'notification_type', 'is_read', 'timestamp')
#     list_filter = ('is_read', 'notification_type', 'timestamp')
#     search_fields = ('user__username', 'message')
#     ordering = ('-timestamp',)
#     readonly_fields = ('timestamp',)
    
#     def message_preview(self, obj):
#         """Display a truncated version of the message in the list view."""
#         return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
#     message_preview.short_description = 'Message'
    
#     def get_queryset(self, request):
#         """Optimize queries with select_related for user."""
#         return super().get_queryset(request).select_related('user')
