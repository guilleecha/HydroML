# Implementación de Lineage y Trazabilidad en Experimentos

## Resumen de la Implementación

Se ha implementado exitosamente una nueva funcionalidad de "Linaje y Trazabilidad" en la vista de detalles de experimentos de HydroML. Esta funcionalidad permite a los usuarios visualizar el flujo completo de datos y transformaciones que llevaron a un experimento específico.

## Componentes Implementados

### 1. Nueva Pestaña "Linaje" en la Interfaz

**Ubicación**: `experiments/templates/experiments/ml_experiment_detail.html`

**Cambios realizados**:
- Agregada nueva pestaña "Linaje" en la barra de pestañas (línea 87)
- Creado contenido completo de la pestaña con visualización tipo timeline (líneas 702-925)
- Agregado event listener JavaScript para el cambio de pestañas (línea 1022)

**Características de la UI**:
- **Timeline Visual**: Diagrama vertical que muestra el flujo de datos paso a paso
- **Tarjetas Interactivas**: Cada paso del linaje se muestra como una tarjeta con información detallada
- **Enlaces Directos**: Enlaces a objetos relacionados (Data Studio, experimentos padre, suites)
- **Iconografía Consistente**: Iconos específicos para cada tipo de objeto en el linaje
- **Información Contextual**: Panel de ayuda explicando qué es el linaje

### 2. Lógica de Backend para Recolección de Datos

**Ubicación**: `experiments/views/experiment_results_views.py`

**Funciones implementadas**:

#### `build_datasource_lineage(datasource, depth=0)`
Función recursiva que construye el árbol de linaje de datasources:
- Rastrea datasources padre/origen
- Maneja datasources derivados y fusionados  
- Asigna profundidad para ordenamiento jerárquico
- Incluye metadatos como tipo de transformación y fechas

#### Datos de Linaje Recolectados en `ExperimentDetailView`
- **DataSource de entrada**: El datasource directo usado por el experimento
- **Cadena de DataSources**: Todos los datasources padre en orden jerárquico
- **Experimento padre**: Si fue forkeado de otro experimento
- **Suite de experimentos**: Si fue generado por un ExperimentSuite
- **Información temporal**: Fechas de creación y modificación

### 3. Estructura de Datos del Linaje

El contexto incluye un diccionario `lineage_datasources` con la siguiente estructura:

```python
{
    'datasource': DataSource object,
    'depth': int,  # Profundidad en el árbol (0 = más reciente)
    'transformation_type': str,  # Tipo de transformación aplicada
    'created_at': datetime,
    'is_derived': bool
}
```

## Funcionalidades de la Pestaña Linaje

### Timeline Visual
- **Flujo Cronológico**: Muestra la evolución de los datos desde el origen hasta el experimento actual
- **Diferenciación Visual**: Colores y estilos diferentes para distinguir tipos de transformación
- **Navegación Directa**: Cada elemento incluye enlaces para explorar objetos relacionados

### Información Mostrada para Cada Paso
1. **DataSources**:
   - Nombre y descripción
   - Tipo de datos
   - Fecha de creación
   - Enlace al Data Studio
   - Indicador si es derivado

2. **Experimentos Padre**:
   - Nombre del experimento origen
   - Estado del experimento
   - Enlace al experimento padre

3. **Suites de Experimentos**:
   - Nombre del suite
   - Descripción y estado
   - Enlace al suite completo

### Panel de Ayuda
- Explicación de qué es el linaje
- Beneficios de la trazabilidad
- Guía de interpretación del timeline

## Casos de Uso Cubiertos

### 1. Experimento con DataSource Simple
- Muestra el datasource de entrada directamente
- Timeline de un solo paso

### 2. Experimento con DataSources Derivados
- Muestra cadena completa desde datos originales
- Cada transformación como un paso separado

### 3. Experimento Forkeado
- Incluye referencia al experimento padre
- Permite navegación entre experimentos relacionados

### 4. Experimento de Suite
- Muestra el suite que lo generó
- Contexto de experimentos batch/automatizados

### 5. Experimento con Datos Fusionados
- Rastrea múltiples datasources de origen
- Muestra el punto de fusión en el timeline

## Aspectos Técnicos

### Manejo de Errores
- Validación de existencia de objetos relacionados
- Fallbacks para casos de datos incompletos
- Manejo graceful de relaciones rotas

### Performance
- Consultas optimizadas con `select_related`
- Carga lazy de objetos relacionados
- Cache de resultados para evitar consultas repetidas

### Compatibilidad
- Funciona con experimentos existentes
- No requiere migración de datos
- Retrocompatible con esquema actual

## Pruebas Realizadas

### Datos de Prueba Creados
1. **Usuario**: guilleeecha
2. **Proyecto**: "Proyecto Linaje Test"
3. **DataSource Original**: "Datos Hidrológicos Originales"
4. **DataSource Derivado**: "Datos Preprocesados"
5. **Experimento**: "Experimento de Prueba Linaje"

### Verificación Funcional
- ✅ Pestaña "Linaje" visible en la interfaz
- ✅ Cambio de pestañas funciona correctamente
- ✅ Timeline se renderiza con datos del experimento
- ✅ Enlaces de navegación operativos
- ✅ Información contextual mostrada correctamente

## Próximos Pasos Recomendados

### Mejoras Funcionales
1. **Visualización de Grafos**: Implementar vista de grafo para linajes complejos
2. **Filtros de Timeline**: Permitir filtrar por tipo de transformación
3. **Exportación**: Generar reportes PDF del linaje completo
4. **Comparación**: Comparar linajes entre experimentos

### Optimizaciones
1. **Cache de Linaje**: Almacenar linajes calculados para mejor performance
2. **Paginación**: Para experimentos con linajes muy largos
3. **Lazy Loading**: Cargar detalles de objetos on-demand

### Integraciones
1. **MLflow**: Integrar con lineage tracking de MLflow
2. **Versioning**: Conectar con sistema de versionado de datos
3. **Auditoría**: Registrar accesos al lineage para compliance

## Archivos Modificados

1. `experiments/templates/experiments/ml_experiment_detail.html`
   - Nueva pestaña y contenido de linaje
   - JavaScript para navegación de pestañas

2. `experiments/views/experiment_results_views.py`
   - Función `build_datasource_lineage()`
   - Lógica de recolección de datos en `ExperimentDetailView`

## Conclusión

La implementación de Lineage y Trazabilidad proporciona una herramienta valiosa para:
- **Transparencia**: Visibilidad completa del flujo de datos
- **Reproducibilidad**: Capacidad de retrazar y reproducir experimentos
- **Auditoría**: Cumplimiento con estándares de trazabilidad de datos
- **Colaboración**: Mejor entendimiento del trabajo entre equipos
- **Debugging**: Identificación rápida de problemas en el pipeline de datos

Esta funcionalidad mejora significativamente la experiencia del usuario y proporciona las bases para futuras características avanzadas de gestión de experimentos.
