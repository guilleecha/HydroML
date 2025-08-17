"""
Query History model for storing user SQL query history in the Data Studio.
"""
import uuid
from django.db import models
from django.conf import settings
from projects.models.datasource import DataSource


class QueryHistory(models.Model):
    """
    Model to store SQL query history for users in the Data Studio.
    
    This model tracks:
    - Which user executed the query
    - Which DataSource the query was executed against
    - The SQL query text
    - When the query was executed
    - Basic metadata about the query execution
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the query history entry"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sql_query_history',
        help_text="User who executed the query"
    )
    
    datasource = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='query_history',
        help_text="DataSource the query was executed against"
    )
    
    sql_query = models.TextField(
        help_text="The SQL query that was executed"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the query was executed"
    )
    
    rows_returned = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of rows returned by the query"
    )
    
    execution_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Query execution time in milliseconds"
    )
    
    was_successful = models.BooleanField(
        default=True,
        help_text="Whether the query executed successfully"
    )
    
    class Meta:
        verbose_name = "Query History"
        verbose_name_plural = "Query Histories"
        ordering = ['-timestamp']  # Most recent first
        indexes = [
            models.Index(fields=['user', 'datasource', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.datasource.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def query_preview(self):
        """Return a truncated version of the query for display purposes."""
        if len(self.sql_query) <= 50:
            return self.sql_query
        return f"{self.sql_query[:47]}..."
    
    @classmethod
    def get_recent_queries(cls, user, datasource=None, limit=10):
        """
        Get recent successful queries for a user, optionally filtered by datasource.
        
        Args:
            user: The user to get queries for
            datasource: Optional DataSource to filter by
            limit: Maximum number of queries to return
            
        Returns:
            QuerySet of QueryHistory objects
        """
        queryset = cls.objects.filter(
            user=user,
            was_successful=True
        )
        
        if datasource:
            queryset = queryset.filter(datasource=datasource)
            
        return queryset[:limit]
