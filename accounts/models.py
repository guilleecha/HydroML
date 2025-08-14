from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    SUBSCRIPTION_LEVELS = [
        ('BASIC', 'Basic'),
        ('ADVANCED', 'Advanced'),
    ]
    subscription_level = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_LEVELS,
        default='BASIC',
        help_text="Nivel de suscripción del usuario"
    )

    # --- Solución al conflicto de nombres ---
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="account_user_groups",  # Nombre único para el acceso inverso
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="account_user_permissions",  # Nombre único para el acceso inverso
        related_query_name="user",
    )
    # --- Fin del bloque de solución ---

    def __str__(self):
        return self.username
