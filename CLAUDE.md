# HydroML - Claude Code CCMP Configuration

> **Primary Directive**: Think carefully and implement the most concise solution that changes as little code as possible.

**📖 FIRST READ**: Complete project rules and guidelines in `.claude/CLAUDE.md`

## 🚀 CCMP SYSTEM ACTIVATED
HydroML uses the official Claude Code PM (CCMP) system. See detailed commands in `.claude/commands/pm/`
Full workflow documentation: `.claude/context/ccmp-workflow.md`

## 🤖 SUB-AGENTS AVAILABLE
Use specialized agents for context optimization. See specifications in `.claude/agents/`
- **file-analyzer**: Log analysis and file summarization  
- **code-analyzer**: Bug hunting and logic tracing
- **test-runner**: Test execution and analysis
- **error-handler**: Automated debugging protocol

**Usage**: Always delegate to appropriate specialist agent for optimal context usage.

## 🔧 MCP SERVERS
Full MCP configuration and status in `.claude/context/mcp-configuration.md`
**Currently operational**: Context7, Sentry, Exa, Filesystem, Playwright, GitHub Official

## Philosophy

### Error Handling
- **Fail fast** for critical configuration (missing text model)
- **Log and continue** for optional features (extraction model)
- **Graceful degradation** when external services unavailable
- **User-friendly messages** through resilience layer

### Testing
- Always use the test-runner agent to execute tests.
- Do not use mock services for anything ever.
- Do not move on to the next test until the current test is complete.
- If the test fails, consider checking if the test is structured correctly before deciding we need to refactor the codebase.
- Tests to be verbose so we can use them for debugging.

## Tone and Behavior

- Criticism is welcome. Please tell me when I am wrong or mistaken, or even when you think I might be wrong or mistaken.
- Please tell me if there is a better approach than the one I am taking.
- Please tell me if there is a relevant standard or convention that I appear to be unaware of.
- Be skeptical.
- Be concise.
- Short summaries are OK, but don't give an extended breakdown unless we are working through the details of a plan.
- Do not flatter, and do not give compliments unless I am specifically asking for your judgement.
- Occasional pleasantries are fine.
- Feel free to ask many questions. If you are in doubt of my intent, don't guess. Ask.

## 🔧 HydroML Specific Configuration

### Docker Environment
- **Always use Docker**: Execute Django commands via `docker compose exec web`
- **Database**: PostgreSQL in container, never use SQLite in production contexts
- **Testing**: Run tests in Docker environment with proper service dependencies

### Development Workflow
- **Foco en la Tarea**: Realiza únicamente los cambios solicitados. Sugiere mejoras, pero no las implementes sin confirmación.
- **Pruebas Rigurosas**: Después de cambios en el backend, SIEMPRE detén cualquier servidor en ejecución e inicia uno nuevo.
- **Context7**: Siempre que necesites consultar documentación de bibliotecas, frameworks o APIs, utiliza la herramienta Context7.

### Django Architecture
- **Models**: Directorio `models/` con archivos separados (no `models.py` único)
- **Views**: Directorio `views/` con archivos separados por funcionalidad  
- **UUID Primary Keys**: Todos los modelos deben usar UUID como clave primaria
- **Services**: Funciones en `services.py` no deben interactuar con `request` directamente
- **Templates**: `{% extends %}` DEBE ser la primera línea, `{% load %}` inmediatamente después

### Package Management
- **uv prioritizado**: `uv venv`, `uv pip install`, `uv pip freeze`
- **pathlib**: Para manipulación de archivos y rutas
- **Sentry**: Para manejo de errores y monitoreo

## ABSOLUTE RULES:

- NO PARTIAL IMPLEMENTATION
- NO SIMPLIFICATION : no "//This is simplified stuff for now, complete implementation would blablabla"
- NO CODE DUPLICATION : check existing codebase to reuse functions and constants Read files before writing new functions. Use common sense function name to find them easily.
- NO DEAD CODE : either use or delete from codebase completely
- IMPLEMENT TEST FOR EVERY FUNCTIONS
- NO CHEATER TESTS : test must be accurate, reflect real usage and be designed to reveal flaws. No useless tests! Design tests to be verbose so we can use them for debuging.
- NO INCONSISTENT NAMING - read existing codebase naming patterns.
- NO OVER-ENGINEERING - Don't add unnecessary abstractions, factory patterns, or middleware when simple functions would work. Don't think "enterprise" when you need "working"
- NO MIXED CONCERNS - Don't put validation logic inside API handlers, database queries inside UI components, etc. instead of proper separation
- NO RESOURCE LEAKS - Don't forget to close database connections, clear timeouts, remove event listeners, or clean up file handles