# Arquitectura del Sistema de Manejo de Sesiones - HydroML Data Studio

## Descripción General

El sistema de manejo de sesiones de HydroML Data Studio es una arquitectura unificada que permite el seguimiento, control y manipulación de transformaciones de datos con capacidades completas de undo/redo. El sistema sigue los principios de CLAUDE.md con módulos enfocados y separación clara de responsabilidades.

## Arquitectura Principal

### 1. Backend Django - Session API

#### Estructura Modular (Post-Refactoring)
```
data_tools/views/api/session_api/
├── __init__.py                     # Configuración del paquete
├── utils.py                        # Utilidades compartidas (DRY principle)
├── session_lifecycle_views.py      # CRUD de sesiones
├── session_operations_views.py     # Undo/Redo y operaciones de historial
├── column_transformation_views.py  # Transformaciones de columnas
└── data_analysis_views.py         # Análisis y estadísticas de datos
```

#### Utilidades Compartidas (`utils.py`)
```python
# Funciones principales para evitar duplicación de código
validate_session_and_datasource()   # Validación unificada
validate_active_session()           # Verificación de sesión activa
format_success_response()           # Respuestas estandarizadas
parse_json_body()                   # Parsing seguro de JSON
log_and_handle_exception()          # Manejo centralizado de errores
```

#### Session Lifecycle (`session_lifecycle_views.py`)
- **initialize_session()**: Crea nueva sesión con DataFrame original
- **get_session_status()**: Estado actual de la sesión
- **clear_session()**: Limpia sesión y libera memoria
- **save_as_new_datasource()**: Persiste estado actual como nuevo dataset

#### Session Operations (`session_operations_views.py`)
- **undo_operation()**: Revierte última transformación
- **redo_operation()**: Reaplica transformación deshecha
- **get_operation_history()**: Historial completo de operaciones

#### Column Transformations (`column_transformation_views.py`)
- **rename_column()**: Renombrar columnas con tracking
- **change_column_type()**: Cambio de tipos con validación
- **fill_missing_values()**: Imputación de valores faltantes
- **drop_columns()**: Eliminación de columnas

### 2. Frontend JavaScript - Modular Architecture

#### Estructura Modular (Post-Refactoring)
```
data_tools/static/data_tools/js/sidebar/
├── DataStudioSidebarController.js   # Controlador principal (orchestrator)
├── UIStateManager.js               # Estado de UI y interacciones
├── SessionManager.js               # Comunicación con session API
├── ColumnOperationsManager.js       # Operaciones de columnas
├── DataAnalysisManager.js          # Análisis y estadísticas
└── IntegrationManager.js           # Integración con TanStack Table
```

#### Controlador Principal
```javascript
class DataStudioSidebarController {
    constructor() {
        this.api = new DataStudioAPI();
        this.sessionManager = new SessionManager(this.api);
        this.columnOpsManager = new ColumnOperationsManager(this.api);
        this.dataAnalysisManager = new DataAnalysisManager(this.api);
        this.uiStateManager = new UIStateManager();
        this.integrationManager = new IntegrationManager();
    }
}
```

## Patrón de Integración de Sesiones

### Flujo Estándar para Operaciones
```javascript
// 1. Validación de sesión
const isValid = await this.sessionManager.validateSession();

// 2. Ejecutar operación
const result = await this.api.executeOperation(params);

// 3. Actualizar historial automáticamente (server-side)
// 4. Actualizar UI
this.updateUI(result);

// 5. Actualizar estado de undo/redo
this.updateUndoRedoState();
```

### Operaciones Conectadas al Sistema
- ✅ **showQuickStats()**: Estadísticas rápidas con tracking
- ✅ **renameColumn()**: Renombrado con historial
- ✅ **changeColumnType()**: Cambio de tipo con validación
- ✅ **fillMissingValues()**: Imputación con tracking
- ✅ **dropColumns()**: Eliminación con posibilidad de undo
- ✅ **applyFilter()**: Filtros con estado persistente

## Servicios de Soporte

### UnifiedSessionManager
```python
# Servicio principal para manejo de sesiones
class UnifiedSessionManager:
    def get_active_session()      # Sesión activa por usuario
    def create_session()          # Nueva sesión con metadata
    def update_session()          # Actualización de estado
    def add_to_history()          # Tracking de operaciones
    def undo_last_operation()     # Revertir cambios
    def redo_operation()          # Rehacer operación
```

### Session Cache (Redis)
- **Almacenamiento temporal**: DataFrames en memoria para performance
- **Historial de operaciones**: Stack de transformaciones
- **Metadata de sesión**: Estado, timestamps, usuario
- **TTL configurado**: Limpieza automática de sesiones inactivas

## Características Técnicas

### Compliance con CLAUDE.md
- **Archivos ≤500 líneas**: session_api_views.py refactorizado (670→5 archivos)
- **Clases ≤100 líneas**: Managers especializados
- **Funciones ≤50 líneas**: Lógica atómica y enfocada
- **DRY Principle**: utils.py centraliza funciones compartidas

### Manejo de Errores
- **Rate limiting**: Protección contra abuso
- **Performance monitoring**: Tracking de tiempos de respuesta
- **Graceful degradation**: Continua funcionando sin sesiones
- **User-friendly messages**: Errores comprensibles para usuario

### Integración con TanStack Table
- **Real-time updates**: Cambios reflejados inmediatamente
- **State synchronization**: UI sincronizada con backend
- **Event-driven**: Comunicación mediante eventos custom

## API Endpoints

### Session Management
```
POST /api/session/{datasource_id}/initialize/     # Inicializar sesión
GET  /api/session/{datasource_id}/status/         # Estado de sesión
POST /api/session/{datasource_id}/clear/          # Limpiar sesión
POST /api/session/{datasource_id}/save/           # Guardar como nuevo dataset
```

### History Operations
```
POST /api/session/{datasource_id}/undo/           # Deshacer operación
POST /api/session/{datasource_id}/redo/           # Rehacer operación
GET  /api/session/{datasource_id}/history/        # Historial completo
```

### Column Operations
```
POST /api/session/{datasource_id}/rename-column/       # Renombrar columna
POST /api/session/{datasource_id}/change-column-type/  # Cambiar tipo
POST /api/session/{datasource_id}/fill-missing/        # Llenar valores faltantes
POST /api/session/{datasource_id}/drop-columns/        # Eliminar columnas
```

## Beneficios de la Arquitectura

1. **Modularidad**: Cada componente tiene una responsabilidad específica
2. **Testability**: Módulos pequeños facilitan testing unitario
3. **Maintainability**: Fácil localización y corrección de bugs
4. **Scalability**: Nuevas operaciones se agregan sin afectar existentes
5. **Performance**: Cache en Redis optimiza operaciones frecuentes
6. **User Experience**: Undo/Redo completo mejora flujo de trabajo

## Implementación Completada - Task 002

- ✅ **Auditoría completa**: ~80% operaciones ahora conectadas
- ✅ **Refactoring arquitectónico**: Compliance total con CLAUDE.md
- ✅ **Integration testing**: Todas las operaciones funcionando
- ✅ **Session persistence**: Estado mantenido entre operaciones
- ✅ **Error handling**: Manejo robusto de casos edge

---

**Última actualización**: 23 de agosto de 2025
**Task completada**: Epic #81 - Task 002: Toolbox-Session Integration
**Arquitectura validada**: Cumple principios CLAUDE.md y patrones Django