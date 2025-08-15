from django.db import models
from .datasource import DataSource

class Transformation(models.Model):
    """
    Represents a transformation applied to a data source to create a derived data source.
    """
    derived_datasource = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='transformations',
        help_text="The derived data source resulting from this transformation."
    )
    order = models.PositiveIntegerField(help_text="The execution order of the transformation.")
    operation_type = models.CharField(
        max_length=50,
        help_text="The type of transformation operation (e.g., 'select_columns', 'filter_rows', 'merge')."
    )
    parameters = models.JSONField(help_text="Arguments for the transformation operation (e.g., {'columns': ['col1', 'col2']}).")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('derived_datasource', 'order')
        ordering = ['order']  # Ensures transformations are executed in the correct order

    def __str__(self):
        return f"Step {self.order}: {self.operation_type}"