# HydroML - Technical Overview

## Architecture Overview

HydroML is a comprehensive machine learning platform built with Django that provides data analysis, experiment management, and model development capabilities.

### Core Components

#### 1. Django Applications
- **core**: Base application with authentication, navigation, and shared utilities
- **projects**: Project and data source management
- **data_tools**: Data analysis, cleaning, and preparation tools
- **experiments**: ML experiment tracking and management
- **connectors**: Database connection and data import functionality
- **accounts**: User authentication and profile management

#### 2. Technology Stack
- **Backend**: Django 5.2.4, Python 3.11+
- **Database**: PostgreSQL 14
- **Caching/Queue**: Redis 6
- **Task Processing**: Celery
- **ML Tracking**: MLflow 2.22.1
- **Frontend**: Tailwind CSS, Alpine.js, AG Grid
- **Visualization**: Plotly.js
- **Containerization**: Docker & Docker Compose

#### 3. Key Features
- **Data Studio**: Interactive data exploration and cleaning interface
- **Experiment Management**: Full ML experiment lifecycle tracking
- **Data Sources**: Support for CSV, Parquet, Excel, and database connections
- **Real-time Processing**: Celery-based background task processing
- **Session Management**: Stateful data transformation sessions
- **Responsive UI**: Modern, dark-theme compatible interface

### Security Features
- CSRF protection
- XSS filtering
- Content type validation
- Secure headers (HSTS, X-Frame-Options)
- Environment-based configuration
- Sentry error monitoring integration

### Database Schema
- UUID primary keys for all models
- Many-to-many relationships between projects and data sources
- Comprehensive audit trails
- Optimized indexing for performance

### API Architecture
- RESTful API endpoints
- JSON-based communication
- Pagination support
- Real-time status updates
- Comprehensive error handling

### Testing Strategy
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- E2E tests in `tests/e2e/`
- Management command tests in `tests/management_commands/`

### Performance Optimizations
- Client-side data grid rendering with AG Grid
- Lazy loading of large datasets
- Redis caching for frequently accessed data
- Optimized database queries
- Static file compression and optimization

## Development Guidelines

### Code Organization
- Modular Django apps with clear responsibilities
- Service layer pattern for business logic
- Repository pattern for data access
- Dedicated API views for frontend communication

### Security Best Practices
- Environment variable configuration
- Secure default settings
- Input validation and sanitization
- Regular dependency updates
- Comprehensive logging and monitoring

### Performance Considerations
- Database query optimization
- Caching strategies
- Asynchronous task processing
- Client-side rendering for complex UIs
- Resource optimization and compression