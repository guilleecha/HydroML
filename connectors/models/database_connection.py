# connectors/models/database_connection.py

import uuid
from django.db import models
from django.contrib.auth.models import User
from ..fields import EncryptedCharField


class DatabaseConnection(models.Model):
    """Model for storing database connection configurations."""
    
    DATABASE_TYPES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='database_connections')
    name = models.CharField(max_length=255, help_text="Friendly name for this connection")
    database_type = models.CharField(max_length=20, choices=DATABASE_TYPES)
    host = models.CharField(max_length=255, blank=True, null=True, help_text="Database host (not required for SQLite)")
    port = models.PositiveIntegerField(blank=True, null=True, help_text="Database port (not required for SQLite)")
    database_name = models.CharField(max_length=255, help_text="Name of the database")
    username = models.CharField(max_length=255, blank=True, null=True, help_text="Database username (not required for SQLite)")
    password = EncryptedCharField(max_length=500, blank=True, null=True, help_text="Database password (encrypted)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Database Connection"
        verbose_name_plural = "Database Connections"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.database_type})"
    
    @property
    def connection_string(self):
        """Generate a connection string for this database configuration."""
        if self.database_type == 'postgresql':
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        elif self.database_type == 'mysql':
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        elif self.database_type == 'sqlite':
            return f"sqlite:///{self.database_name}"
        return None
    
    def test_connection(self):
        """Test if this database connection is valid."""
        try:
            import sqlalchemy
            engine = sqlalchemy.create_engine(self.connection_string)
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
