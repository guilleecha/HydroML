import uuid
import os
from django.db import models

class DataSourceType(models.TextChoices):
    """Define los tipos de fuentes de datos según su etapa en el pipeline."""
    ORIGINAL = 'ORIGINAL', 'Original'
    PREPARED = 'PREPARED', 'Preparado'
    FUSED = 'FUSED', 'Fusionado'

class DataSource(models.Model):
    """
    Representa un archivo de datos (CSV) que puede ser utilizado por múltiples proyectos.
    Este es el "activo" fundamental sobre el que se trabaja.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Temporary: Keep project field for migration
    project = models.ForeignKey(
        'projects.Project', 
        on_delete=models.CASCADE, 
        related_name='datasources_temp',
        help_text="Temporary project relationship during migration"
    )
    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name="owned_datasources",
        help_text="User who owns this DataSource",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, verbose_name="Nombre de la Fuente de Datos")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    file = models.FileField(
        upload_to='datasources/%Y/%m/', 
        blank=True, 
        null=True  # Ahora el campo es opcional
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data_type = models.CharField(
        max_length=10,
        choices=DataSourceType.choices,
        default=DataSourceType.ORIGINAL,
        verbose_name="Tipo de Dato"
    )

    class Status(models.TextChoices):
        UPLOADING = 'UPLOADING', 'Subiendo'
        PROCESSING = 'PROCESSING', 'Procesando'
        READY = 'READY', 'Listo'
        ERROR = 'ERROR', 'Error'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADING
    )

    quality_report = models.JSONField(
        null=True,
        blank=True,
        help_text="Stores the data quality analysis results."
    )

    quality_report_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to the Great Expectations HTML quality report"
    )
    
    # Flags de calidad por columna para validaciones ML
    column_flags = models.JSONField(
        null=True, blank=True,
        help_text="Flags de calidad por columna para validaciones ML",
        default=dict
    )

    # AJUSTE 2: Relación de Linaje (ManyToManyField)
    # Esta relación es poderosa. Significa que un DataSource puede ser el resultado
    # de la combinación de VARIOS padres. Ideal para la fusión de datos.
    parents = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='children',
        verbose_name="Fuentes de Datos de Origen (Padres)"
    )

    # Nueva relación para indicar si es una fuente de datos derivada
    is_derived = models.BooleanField(default=False, help_text="True si esta es una fuente de datos derivada.")

    # Recipe Builder: Almacena los pasos de transformación aplicados
    recipe_steps = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de pasos de transformación aplicados a esta fuente de datos"
    )

    # Missing Data Toolkit: Almacena el análisis profundo de datos faltantes
    missing_data_report = models.JSONField(
        null=True,
        blank=True,
        help_text="Stores deep missing data analysis results including feature importance and combination counts"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # AJUSTE 3: Buenas prácticas
        verbose_name = "Fuente de Datos"
        verbose_name_plural = "Fuentes de Datos"
        ordering = ['-uploaded_at']

    @property
    def filename(self):
        """Devuelve solo el nombre del archivo, sin la ruta."""
        if self.file:
            return os.path.basename(self.file.name)
        return ""

    @property
    def total_rows(self):
        """Returns the total number of rows in the dataset."""
        if not self.file:
            return 0
        try:
            import pandas as pd
            file_path = self.file.path
            if file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='latin-1')
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_parquet(file_path)  # Fallback
            return len(df)
        except Exception:
            return 0

    @property
    def total_columns(self):
        """Returns the total number of columns in the dataset."""
        if not self.file:
            return 0
        try:
            import pandas as pd
            file_path = self.file.path
            if file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='latin-1')
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_parquet(file_path)  # Fallback
            return len(df.columns)
        except Exception:
            return 0

    def __str__(self):
        return self.name or f"Fuente de datos {self.id}"