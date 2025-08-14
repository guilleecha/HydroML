from django.db import models
from django.conf import settings
# Asegúrate de haber instalado django-cryptography: pip install django-cryptography
from .fields import EncryptedCharField  # <--- Asegúrate de que importe desde .fields

class DatabaseConnection(models.Model):
    """
    Almacena de forma segura las credenciales para una conexión
    a una base de datos externa.
    """
    DATABASE_TYPE_CHOICES = [
        ('POSTGRESQL', 'PostgreSQL'),
        ('MYSQL', 'MySQL'),
        ('SQLITE', 'SQLite'),
        # Puedes añadir más tipos en el futuro
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='database_connections'
    )
    name = models.CharField(
        max_length=100,
        help_text="Un nombre descriptivo para esta conexión."
    )
    database_type = models.CharField(
        max_length=20,
        choices=DATABASE_TYPE_CHOICES
    )
    host = models.CharField(max_length=100)
    port = models.PositiveIntegerField()
    database_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = EncryptedCharField(max_length=512) # Usamos un max_length mayor para el texto encriptado



    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        # Evita que un usuario cree dos conexiones con el mismo nombre
        unique_together = ('user', 'name')
        ordering = ['-created_at']
