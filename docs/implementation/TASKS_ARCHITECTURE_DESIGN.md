# Tasks Architecture Design - HydroML

## Problema Actual
- Funciones >50 líneas violando CLAUDE.md
- Archivos fragmentados y desorganizados
- Import de `tasks_old.py` inexistente
- Lógica compleja mezclada en tasks
- Falta de separación clara de responsabilidades

## Nueva Arquitectura Propuesta

### 1. Estructura de Directorios
```
data_tools/
├── tasks/
│   ├── __init__.py                     # Exportaciones principales
│   ├── base.py                         # Clases base y decoradores
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── file_loaders.py            # Carga de archivos
│   │   ├── format_detection.py        # Detección de formatos
│   │   ├── ingestion_tasks.py         # Tasks principales
│   │   └── report_generators.py       # Generadores de reportes
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── data_transformers.py       # Transformaciones de datos
│   │   ├── processing_tasks.py        # Tasks de procesamiento
│   │   └── pipeline_orchestrator.py   # Orquestación de pipelines
│   ├── quality/
│   │   ├── __init__.py
│   │   ├── analyzers.py               # Análisis de calidad
│   │   ├── quality_tasks.py           # Tasks de calidad
│   │   ├── missing_data_analyzer.py   # Análisis de datos faltantes
│   │   └── visualization_generators.py # Generadores de visualizaciones
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py              # Decoradores para tasks
│       ├── exceptions.py              # Excepciones personalizadas
│       └── validators.py              # Validadores
```

### 2. Principios de Diseño

#### A. Separación de Responsabilidades
- **Tasks**: Solo coordinación y manejo de errores
- **Services**: Lógica de negocio
- **Utilities**: Funciones auxiliares reutilizables

#### B. Cumplimiento de CLAUDE.md
- Funciones ≤50 líneas
- Clases ≤100 líneas  
- Archivos ≤500 líneas
- Una responsabilidad por función

#### C. Manejo de Errores Robusto
- Try-catch en cada task
- Logging detallado
- Actualización de estados en BD
- Reportes de error estructurados

#### D. Modularidad y Reutilización
- Componentes intercambiables
- Interfaces claras
- Dependency injection
- Configuración externa

### 3. Patrones de Implementación

#### A. Task Base Class
```python
from abc import ABC, abstractmethod
from celery import shared_task
import logging

class BaseTask(ABC):
    """Clase base para todos los tasks."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Lógica principal del task."""
        pass
    
    def handle_error(self, error, datasource_id=None):
        """Manejo estándar de errores."""
        pass
    
    def update_status(self, datasource, status, report=None):
        """Actualización estándar de estado."""
        pass
```

#### B. Task Decorator Pattern
```python
def robust_task(task_name: str):
    """Decorador para tasks robustos con manejo de errores."""
    def decorator(func):
        @shared_task
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Setup logging, error handling, etc.
            pass
        return wrapper
    return decorator
```

#### C. Pipeline Pattern
```python
class DataPipeline:
    """Pipeline modular para procesamiento de datos."""
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, step):
        """Agregar paso al pipeline."""
        pass
    
    def execute(self, data):
        """Ejecutar pipeline completo."""
        pass
```

### 4. Casos de Uso Principales

#### A. Ingesta de Datos
1. **Detección de formato** → `format_detection.py`
2. **Carga de archivo** → `file_loaders.py`
3. **Validación básica** → `validators.py`
4. **Conversión a Parquet** → `data_transformers.py`
5. **Generación de reporte** → `report_generators.py`

#### B. Análisis de Calidad
1. **Análisis estadístico** → `analyzers.py`
2. **Detección de anomalías** → `analyzers.py`
3. **Análisis de datos faltantes** → `missing_data_analyzer.py`
4. **Generación de visualizaciones** → `visualization_generators.py`
5. **Reporte HTML** → `report_generators.py`

#### C. Procesamiento ML
1. **Preparación de datos** → `data_transformers.py`
2. **Feature engineering** → `data_transformers.py`
3. **Validación ML** → `validators.py`
4. **Pipeline orchestration** → `pipeline_orchestrator.py`

### 5. Beneficios de la Nueva Arquitectura

1. **Mantenibilidad**: Código modular y bien organizado
2. **Testabilidad**: Componentes pequeños y enfocados
3. **Escalabilidad**: Fácil agregar nuevos tipos de tasks
4. **Reutilización**: Componentes intercambiables
5. **Debugging**: Logs estructurados y manejo de errores claro
6. **Cumplimiento**: Respeta límites de CLAUDE.md

### 6. Plan de Migración

1. **Fase 1**: Crear estructura base y utilidades
2. **Fase 2**: Migrar tasks de ingesta
3. **Fase 3**: Migrar tasks de calidad
4. **Fase 4**: Migrar tasks de procesamiento
5. **Fase 5**: Testing y validación
6. **Fase 6**: Cleanup de código legacy

### 7. Configuración Externa

```python
# tasks_config.py
INGESTION_CONFIG = {
    'supported_formats': ['.csv', '.xlsx', '.json', '.parquet'],
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'encoding_fallbacks': ['utf-8', 'latin-1', 'cp1252'],
    'quality_checks_enabled': True
}

QUALITY_CONFIG = {
    'missing_data_threshold': 0.5,
    'outlier_detection_method': 'iqr',
    'visualization_sample_size': 1000,
    'report_template': 'quality_report_template.html'
}
```

Esta arquitectura proporcionará una base sólida, mantenible y escalable para todos los tasks del sistema.