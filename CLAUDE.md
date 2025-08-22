# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Primary Directive**: Think carefully and implement the most concise solution that changes as little code as possible.

**📖 FIRST READ**: Complete project rules and guidelines in `.claude/CLAUDE.md`

## USE SUB-AGENTS FOR CONTEXT OPTIMIZATION

### 1. Always use the file-analyzer sub-agent when asked to read files.
The file-analyzer agent is an expert in extracting and summarizing critical information from files, particularly log files and verbose outputs. It provides concise, actionable summaries that preserve essential information while dramatically reducing context usage.

### 2. Always use the code-analyzer sub-agent when asked to search code, analyze code, research bugs, or trace logic flow.

The code-analyzer agent is an expert in code analysis, logic tracing, and vulnerability detection. It provides concise, actionable summaries that preserve essential information while dramatically reducing context usage.

### 3. Always use the test-runner sub-agent to run tests and analyze the test results.

Using the test-runner agent ensures:

- Full test output is captured for debugging
- Main conversation stays clean and focused
- Context usage is optimized
- All issues are properly surfaced
- No approval dialogs interrupt the workflow

## 🚀 CCMP SYSTEM ACTIVATED
HydroML uses the official Claude Code PM (CCMP) system. See detailed commands in `.claude/commands/pm/`
Full workflow documentation: `.claude/context/ccmp-workflow.md`

### 🌳 CCMP Worktrees for Safe Development
**ALWAYS use worktrees for feature development to avoid conflicts with main branch:**

#### Epic-Level Development (Recommended)
```bash
/pm:epic-start <epic-name>    # Creates worktree with parallel agents
/pm:epic-status <epic-name>   # Monitor progress
/pm:epic-merge <epic-name>    # Merge back to main when complete
```

#### Issue-Level Development  
```bash
/pm:issue-start <issue-number>  # Launch specialized agents for single issue
```

#### Manual Branch Creation
```bash
git checkout -b feature/<feature-name>  # Traditional branch workflow
```

**Worktree Structure:**
- **Location**: `../epic-{name}` (sibling directory)
- **Branch Format**: `epic/feature-name`
- **Parallel Agents**: Multiple agents work simultaneously in same worktree
- **Safe Isolation**: Complete separation from main branch until merge

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

## 🔧 Common Development Commands

### Docker Commands (Primary Development Environment)
```bash
# Start all services
docker-compose up --build

# Django commands in container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py shell

# Restart services after backend changes
docker-compose down && docker-compose up --build

# View logs
docker-compose logs web
docker-compose logs worker
```

### Testing Commands
```bash
# Run all tests with coverage
docker-compose exec web python -m pytest

# Run specific test categories
docker-compose exec web python -m pytest tests/unit/
docker-compose exec web python -m pytest tests/integration/
docker-compose exec web python -m pytest tests/e2e/

# Run tests with specific markers
docker-compose exec web python -m pytest -m "unit"
docker-compose exec web python -m pytest -m "integration"

# Generate coverage report
docker-compose exec web python -m pytest --cov=. --cov-report=html
```

### Frontend Development
```bash
# Build CSS (Tailwind)
npm run build          # Production build
npm run dev            # Development with watch

# Install frontend dependencies
npm install
```

### Code Quality
```bash
# Format and lint (in container)
docker-compose exec web black .
docker-compose exec web isort .
docker-compose exec web flake8 .
```

## 🏗️ Architecture Overview

### Core Django Apps Structure
- **core/**: Authentication, navigation, shared utilities, design system components
- **projects/**: Project and datasource management with many-to-many relationships
- **data_tools/**: Data analysis, cleaning, preparation with session-based workflows
- **experiments/**: ML experiment tracking with MLflow integration
- **connectors/**: Database connections and data import functionality
- **accounts/**: User management and profiles

### Key Architectural Patterns
- **Models**: Split into `models/` directories with separate files (not single `models.py`)
- **Views**: Split into `views/` directories organized by functionality
- **Services**: Business logic separated into `services.py` and `services/` directories
- **UUID Primary Keys**: All models use UUID for primary keys
- **Template Structure**: All templates must start with `{% extends %}` followed by `{% load %}`

### Technology Stack
- **Backend**: Django 5.2.4, PostgreSQL 14, Redis 6, Celery
- **Frontend**: Tailwind CSS, Alpine.js, AG Grid, Plotly.js
- **ML/Analytics**: MLflow 2.22.1, Optuna, scikit-learn, pandas
- **Infrastructure**: Docker Compose, Sentry (monitoring)

### Service Dependencies
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache and task queue (port 6379)
- **MLflow**: Experiment tracking (port 5000)
- **Web App**: Django application (port 8000)
- **Celery Worker**: Background task processing

## 🔧 HydroML Specific Configuration

### Docker Environment Requirements
- **Always use Docker**: Execute Django commands via `docker compose exec web`
- **Database**: PostgreSQL in container, never use SQLite in production contexts
- **Testing**: Run tests in Docker environment with proper service dependencies
- **Service Health**: Ensure all services (db, redis, mlflow) are healthy before running commands

### Development Workflow
- **Focused Changes**: Make only requested changes, suggest improvements but don't implement without confirmation
- **Rigorous Testing**: After backend changes, always restart services with `docker-compose down && docker-compose up --build`
- **Context7**: Always use Context7 tool for library/framework documentation queries

### Django Architecture Conventions
- **Models**: Use `models/` directory structure with separate files
- **Views**: Use `views/` directory structure with functional separation
- **UUID Primary Keys**: All models must use UUID as primary key
- **Services**: Business logic in `services.py` should not interact with `request` objects directly
- **Templates**: Must start with `{% extends %}` as first line, `{% load %}` immediately after

### Package Management
- **uv prioritized**: Use `uv venv`, `uv pip install`, `uv pip freeze` when possible
- **pathlib**: Use for file and path manipulation
- **Sentry**: Integrated for error handling and monitoring

### Component Library Strategy
- **Always check Grove components first**: Search `core/static/core/css/components/` before creating new CSS
- **Grove over Wave**: Use Grove Design System components (modern) over Wave components (legacy)
- **Component Hierarchy**:
  1. **Grove components** - Primary system with design tokens
  2. **Specialized components** - Domain-specific (data-studio, ml-wizard)
  3. **Wave components** - Legacy only, avoid for new features
- **Before creating new CSS**: Search existing components in this order:
  1. Grove system (`grove-*.css`)
  2. Specialized components (`*-components.css`) 
  3. Wave legacy (`wave-components.css`)
- **CSS best practices**: Use semantic class names, design tokens, avoid Tailwind utilities in templates

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

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.