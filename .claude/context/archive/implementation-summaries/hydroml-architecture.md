# HydroML Architecture Context

## Project Overview
HydroML is a comprehensive ML-powered data analysis platform built with Django, focusing on data quality, experiment tracking, and feature engineering.

## Technology Stack

### Backend
- **Django 5.2.4** - Main web framework
- **PostgreSQL 14** - Primary database
- **Redis 6** - Caching and session storage
- **Celery** - Background task processing
- **MLflow 2.22.1** - ML experiment tracking
- **Optuna** - Hyperparameter optimization

### Frontend
- **Alpine.js** - Reactive JavaScript framework
- **Tailwind CSS** - Utility-first CSS framework
- **AG Grid** - Advanced data grid component
- **Plotly.js** - Interactive visualizations

### Infrastructure
- **Docker Compose** - Development environment
- **uv** - Python package management
- **Node.js/npm** - Frontend asset management

## Application Structure

### Core Apps
- **core** - Authentication, navigation, dashboard, shared utilities
- **projects** - Project and DataSource management with M2M relationships
- **data_tools** - Data Studio, quality pipeline, session management
- **experiments** - MLflow integration, ML experiment tracking
- **connectors** - Database connections and data import functionality
- **accounts** - User authentication and profile management

### Key Patterns
- Models use UUID primary keys
- Views organized in separate directories, not single files
- Services layer separated from Django request handling
- Modular API structure with specialized endpoints
- Component-based frontend architecture

## Recent Improvements
- Complete DataSource-Project many-to-many refactoring
- Unified Data Studio dashboard with context-aware navigation
- Modular class-based API architecture
- One Dark theme and enhanced UI/UX features
- Docker environment and major architectural refactors

## Development Workflow
1. Use Docker Compose for consistent environment
2. Run migrations after model changes
3. Restart Django server after backend changes
4. Use npm run dev for Tailwind CSS watching
5. Run tests in isolated Docker environment

## Code Quality Standards
- Functions: max 50 lines
- Classes: max 100 lines
- Files: max 500 lines
- Test coverage: >80% required
- Follow CLAUDE.md guidelines strictly

## Security Configuration
- Environment variables for all secrets
- CSRF protection enabled
- Sentry error monitoring configured
- HTTPS enforcement for production