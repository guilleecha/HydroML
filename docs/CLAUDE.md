# HydroML - Claude Code PM Instructions

## 🚀 CCPM SYSTEM ACTIVATED
**HydroML now uses the official Claude Code PM (CCPM) system from automazeio for spec-driven development with parallel AI agents.**

### Available CCPM Commands
```bash
/pm:prd-new <feature-name>      # Create Product Requirements Document
/pm:prd-parse <feature-name>    # Convert PRD to Epic implementation plan
/pm:epic-decompose <feature>    # Break epic into parallel tasks
/pm:epic-sync <feature>         # Sync tasks to GitHub Issues (requires gh CLI)
/pm:issue-start <issue-number>  # Launch parallel specialist agents
/pm:sub-issue <command> <args>  # Manage sub-issue hierarchies (requires gh-sub-issue)
```

### CCPM Workflow
1. **Brainstorm** → PRD creation
2. **Document** → Epic specification  
3. **Plan** → Task decomposition
4. **Sync** → GitHub Issues integration with hierarchical sub-issues
5. **Execute** → Parallel agent implementation

### 📊 Sub-Issue Management (gh-sub-issue)
**Extension installed**: `yahsan2/gh-sub-issue v0.3.0`

Create hierarchical task structures with automatic parent-child relationships:
```bash
# List epic progress
gh sub-issue list 7    # Data Studio Enhancements (6 tasks)
gh sub-issue list 14   # Wave Theme Integration (8 tasks)

# Manual sub-issue management
gh sub-issue add <epic-number> <task-number>     # Link existing issue
gh sub-issue create --parent <epic> --title "Task Name"  # Create new
gh sub-issue remove <epic-number> <task-number>  # Unlink
```

**Current Epic Structure:**
- **Epic #7**: Data Studio Enhancements → Sub-issues #8-#13 (6 tasks)
- **Epic #14**: Wave Theme Integration → Sub-issues #15-#22 (8 tasks)

## Filosofía General

### Principios de Desarrollo
- **Simplicidad Primero (KISS)**: Prioriza siempre la solución más simple, clara y legible. Evita la complejidad innecesaria.
- **No lo Necesitarás (YAGNI)**: Implementa funcionalidades solo cuando sean necesarias, no por especulación futura.
- **Evitar la Duplicación (DRY)**: No repitas código. Refactoriza en funciones o clases reutilizables.
- **Iterar, no Recrear**: Antes de escribir código nuevo, busca en el workspace funcionalidades similares que puedas extender.

### Principios de Diseño
- **Responsabilidad Única**: Cada función, clase y módulo debe tener un propósito claro.
- **Inversión de Dependencias**: Los módulos de alto nivel no deben depender de módulos de bajo nivel.
- **Abierto/Cerrado**: Las entidades de software deben estar abiertas para extensión pero cerradas para modificación.
- **Fallar Rápido**: Detecta errores temprano y lanza excepciones inmediatamente cuando ocurran problemas.

## Estructura y Calidad del Código

### Límites de Archivos y Funciones
- **Archivos**: Máximo 500 líneas de código. Si se supera, refactorizar dividiendo en módulos.
- **Funciones**: Máximo 50 líneas con una responsabilidad clara y única.
- **Clases**: Máximo 100 líneas representando un solo concepto o entidad.
- **Módulos**: Organizar código en módulos claramente separados, agrupados por característica o responsabilidad.

### Estándares de Formato
- **Indentación**: Utiliza 4 espacios para la indentación en Python.
- **Código Limpio**: Si introduces un nuevo patrón, elimina la implementación anterior para evitar código muerto.
- **Comentarios**: Escribe comentarios concisos para explicar el "porqué" de lógicas complejas.
- **Variables de Entorno**: Utiliza variables de entorno para configuraciones, nunca hardcodees valores sensibles.

## Metodología de Trabajo

### Proceso de Desarrollo
- **Foco en la Tarea**: Realiza únicamente los cambios solicitados. Sugiere mejoras, pero no las implementes sin confirmación.
- **Pruebas Rigurosas**: Después de cambios en el backend, SIEMPRE detén cualquier servidor en ejecución e inicia uno nuevo.
- **Claridad Ante Todo**: Si una solicitud es ambigua, haz preguntas para clarificar los requisitos.

### Consulta de Documentación
- **Context7**: Siempre que necesites consultar documentación de bibliotecas, frameworks o APIs, utiliza la herramienta Context7 para obtener información actualizada y precisa.
- **Investigación Previa**: Antes de implementar funcionalidad nueva, consulta la documentación relevante para entender las mejores prácticas.

## Manejo de Errores y Monitoreo

### Sentry para Manejo de Errores
- **Logging de Errores**: Todo el manejo de errores debe implementarse utilizando Sentry como herramienta principal.
- **Captura de Excepciones**: Utiliza Sentry para capturar y reportar excepciones en producción.
- **Contexto de Errores**: Incluye información contextual relevante en los reportes de error de Sentry.
- **Monitoreo Proactivo**: Configura alertas apropiadas en Sentry para detectar problemas temprano.

## Reglas Específicas de HydroML

### Modelos y Base de Datos
- Todos los modelos de Django deben tener un campo ID de tipo UUID como clave primaria.
- Para la manipulación de archivos y rutas, utiliza siempre la biblioteca `pathlib`.
- Las funciones de servicio (`services.py`) nunca deben interactuar directamente con el objeto `request` de Django; deben recibir los datos que necesitan como parámetros.

### Gestión de Entornos y Paquetes (uv)
- Para cualquier tarea relacionada con entornos virtuales o paquetes de Python, prioriza siempre el uso de `uv`.
- Para crear entornos virtuales: `uv venv`
- Para instalar paquetes: `uv pip install <package_name>`
- Para instalar desde requirements: `uv pip install -r requirements.txt`
- Para generar requirements: `uv pip freeze > requirements.txt`

## Arquitectura y Estructura del Proyecto

### Organización de Django
- Los modelos no deben estar en un único archivo `models.py`. Crear un directorio `models/` donde cada modelo reside en su propio archivo (ej. `project.py`, `datasource.py`).
- Lo mismo aplica para las vistas: deben estar en un directorio `views/` en archivos separados.
- Asegúrate de que los archivos `__init__.py` correspondientes importen todos los módulos para que Django pueda descubrirlos.

### Reglas para Plantillas de Django
- La etiqueta `{% extends '...' %}` DEBE SER SIEMPRE la primera línea de cualquier plantilla, sin excepciones.
- Cualquier etiqueta `{% load ... %}` debe ir INMEDIATAMENTE DESPUÉS de la etiqueta `{% extends %}`.
- Al usar `django-crispy-forms`:
  - Filtro para un solo campo: `|as_crispy_field` (nunca uses `|as_field`)
  - Filtro para formulario completo: `|crispy`
  - Cargar filtros con: `{% load tailwind_filters %}`