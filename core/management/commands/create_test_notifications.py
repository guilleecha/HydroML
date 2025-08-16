from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
# from core.models import Notification
from django.urls import reverse


class Command(BaseCommand):
    help = 'Create test notifications for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user', 
            type=str, 
            help='Username to create notifications for (default: first user)'
        )
        parser.add_argument(
            '--count', 
            type=int, 
            default=3, 
            help='Number of test notifications to create (default: 3)'
        )

    def handle(self, *args, **options):
        # Get the user
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{options['user']}' not found")
                )
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR("No users found in the database")
                )
                return

        # Create test notifications
        count = options['count']
        notifications_created = []

        test_messages = [
            "Tu experimento 'Test Model Training' ha comenzado a ejecutarse.",
            "Tu experimento 'Random Forest Analysis' ha finalizado exitosamente.",
            "Tu experimento 'Linear Regression Test' ha finalizado con errores.",
            "Nuevo dataset 'weather_data.csv' subido exitosamente.",
            "Tu experimento 'Deep Learning Model' ha comenzado a ejecutarse.",
        ]

        for i in range(count):
            message = test_messages[i % len(test_messages)]
            # notification = Notification.objects.create(
            #     user=user,
            #     message=message,
            #     notification_type='experiment',
            #     related_object_id=1,  # Dummy experiment ID
            #     link=reverse('experiments:detail', kwargs={'pk': 'test-experiment-id'}) if 'experimento' in message else None
            # )
            # notifications_created.append(notification)

        self.stdout.write(
            self.style.SUCCESS(
                f"Command disabled - Notification model not implemented yet"
                # f"Successfully created {len(notifications_created)} test notifications for user '{user.username}'"
            )
        )

        # # Display created notifications
        # for notification in notifications_created:
        #     self.stdout.write(f"  - {notification.message[:50]}...")
