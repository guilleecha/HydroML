# HydroML System Architecture - August 2025

**Version**: 2.0 (Post-Grove Migration)  
**Status**: Active Development  
**Last Updated**: August 24, 2025

## System Overview

HydroML is a comprehensive machine learning platform built on Django with a modern component-based frontend architecture. The system has evolved from a basic ML toolkit to a sophisticated data manipulation and experiment management platform.

### Core Philosophy
- **Component-First Design**: Modular, reusable UI components
- **Session-Based Workflows**: Persistent user data manipulation sessions  
- **Modern Web Standards**: Progressive enhancement with Alpine.js
- **Design System Consistency**: Grove Design System for unified UX

## Technology Stack

### Backend Architecture
```
Django 5.2.4
├── PostgreSQL 14        # Primary database
├── Redis 6             # Cache + session storage
├── Celery             # Async task processing (planned)
└── MLflow 2.22.1      # ML experiment tracking
```

### Frontend Architecture
```
Modern Web Stack
├── Tailwind CSS 3.x   # Utility-first CSS framework
├── Alpine.js 3.x      # Reactive JavaScript framework
├── TanStack Table     # Advanced data grid component
└── Grove Design System # Custom component library
```

### Infrastructure
```
Docker Compose
├── Web Container      # Django application (port 8000)
├── Worker Container   # Celery worker (planned)
├── Database Container # PostgreSQL (port 5432)
├── Cache Container    # Redis (port 6379)
└── MLflow Container   # Experiment tracking (port 5000)
```

## Application Architecture

### Django App Structure
```
hydroML/
├── core/              # Authentication, UI components, design system
├── projects/          # Workspace and project management
├── data_tools/        # Data manipulation, cleaning, analysis
├── experiments/       # ML experiment tracking and management
├── connectors/        # Database connections and data import
└── accounts/          # User management and profiles
```

### Design System Hierarchy

#### 1. Grove Design System (Primary)
**Location**: `core/static/core/css/components/grove-*.css`  
**Status**: ✅ Active, Modern, Primary System  
**Components**:
- `grove-card.css` - Container system with semantic variants
- `grove-button.css` - Button components with state management
- `grove-navigation.css` - Navigation and headbar system
- `grove-badge.css` - Status indicators and count displays
- `grove-modal.css` - Dialog and overlay system

**Design Tokens**: CSS custom properties for consistent theming
```css
--grove-primary: #2563eb;
--grove-gray-50: #f9fafb;
--space-4: 1rem;
--radius-md: 0.375rem;
```

#### 2. Specialized Components (Domain-Specific)
**Purpose**: Extend Grove for specific use cases
- `tanstack-table.css` - Data table styling
- `ml-wizard.css` - ML experiment workflow styling
- `grove-session-controls.css` - Data manipulation session UI

#### 3. Wave Components (Legacy - Migration Target)
**Status**: ⚠️ Legacy system, migrate to Grove when possible  
**Location**: `core/static/core/js/components/wave/`

### Template Architecture

#### Base Template Hierarchy
```
Template Inheritance Flow:
base_main.html (Root)
    ├── dashboard.html
    ├── data_sources_list.html
    ├── experiments/*.html
    └── projects/*.html
```

#### Component Template Pattern
```
Reusable Partials:
core/templates/core/partials/
    ├── _grove_enhanced_headbar.html    # Two-row navigation
    ├── _loading_overlay.html           # Global loading states
    ├── _dashboard_stats.html           # Metric cards
    └── _theme_switcher.html            # Theme management
```

## Data Flow Architecture

### Session Management System (Current Evolution)
**Current State**: Multiple competing systems (Issues #81-85)
**Target Architecture**: Unified Redis-based session management

```
Session Flow:
User Action → Session Manager → Redis Cache → Database → Response
                    ↓
            UI State Updates (Alpine.js)
```

### Data Studio Architecture
**Epic #65**: Complete data manipulation tool with 12 planned tasks

```
Data Studio Components:
├── Session Management    # User data manipulation sessions
├── TanStack Table       # Advanced data grid (✅ Implemented)
├── Formula Engine       # Mathematical operations (Planned)
├── Export System        # Multiple format export (Planned)
├── NaN Detection        # Data quality tools (Planned)
└── Column Management    # Data schema manipulation (Planned)
```

### ML Experiment Flow
```
Experiment Pipeline:
Data Import → Data Preparation → Model Training → Evaluation → Results
     ↓              ↓                 ↓            ↓         ↓
Projects App → Data Tools → Experiments App → MLflow → Dashboard
```

## API Architecture

### Current Endpoints
```
REST API Structure:
/api/
├── projects/other/           # Breadcrumb navigation data
├── presets/                  # Hyperparameter preset management  
├── theme/preferences/        # Theme system integration (✅ Recently added)
└── (planned) session/        # Data manipulation sessions
```

### Future API Expansion (Celery Integration)
```
Planned Async APIs:
/api/async/
├── experiments/train/        # Background ML training
├── data/export/             # Large dataset export
├── data/import/             # File processing
└── analysis/generate/       # Report generation
```

## Security Architecture

### Authentication & Authorization
```
Security Stack:
├── Django Authentication    # User management
├── Session-based Auth      # Web sessions
├── CSRF Protection         # Form security
└── Sentry Integration      # Error monitoring
```

### Data Protection
- UUID primary keys across all models
- Secure file handling for data uploads
- Rate limiting on API endpoints (planned)
- Input validation and sanitization

## Performance Architecture

### Caching Strategy
```
Cache Hierarchy:
├── Redis Cache            # Session data, API responses
├── Database Query Cache   # ORM optimization
├── Static File Cache     # CSS/JS/Images
└── Browser Cache         # Client-side caching
```

### Database Optimization
- Selective model prefetching
- Database connection pooling
- Query optimization with select_related/prefetch_related
- UUID primary keys for better distribution

## Deployment Architecture

### Docker Environment
```
Services:
├── web:       Django application server
├── worker:    Celery background worker (planned)  
├── db:        PostgreSQL database
├── redis:     Cache and message broker
└── mlflow:    ML experiment tracking server
```

### Development vs Production
- **Development**: SQLite + file sessions (legacy)
- **Target**: PostgreSQL + Redis sessions
- **Monitoring**: Sentry for error tracking

## File Organization Standards

### CSS Architecture
```
Hierarchy:
core/static/core/css/
├── design-tokens.css          # Foundation variables
├── components/
│   ├── grove-*.css           # Primary component system
│   ├── [domain]-*.css        # Specialized components
│   └── legacy/               # Wave components (migration target)
└── layouts/                   # Page-level layout styles
```

### JavaScript Architecture  
```
Module Organization:
core/static/core/js/
├── theme/                    # Theme management system
├── components/
│   ├── core/                # Base component classes
│   ├── grove/               # Grove component implementations
│   ├── wave/                # Legacy components (migration target)
│   └── [app-specific]/      # Domain components
└── utils/                    # Shared utilities
```

### Template Organization
```
Template Structure:
app/templates/app/
├── base/                    # Base templates and layouts
├── partials/               # Reusable template fragments  
├── components/             # Self-contained UI components
├── pages/                  # Full page templates
└── demos/                  # Development and testing (cleanup target)
```

## Development Workflow

### Component Development Cycle
1. **Design**: Define component in Grove Design System
2. **Implement**: CSS component with design tokens
3. **Template**: Django template integration  
4. **JavaScript**: Alpine.js interactivity (if needed)
5. **Test**: Browser testing with Playwright
6. **Document**: Update context documentation

### Migration Strategy (Wave → Grove)
1. **Audit**: Identify Wave component usage
2. **Map**: Define Grove equivalent components
3. **Implement**: Create Grove replacement
4. **Migrate**: Update templates to use Grove
5. **Remove**: Clean up Wave component files

## Quality Assurance

### Testing Strategy
- **Unit Tests**: Python/Django backend logic
- **Integration Tests**: API endpoint testing
- **Browser Tests**: Playwright for UI validation
- **Performance Tests**: Load testing for data operations

### Code Quality
- **Linting**: Black, isort, flake8 for Python
- **Type Checking**: Django model validation
- **Security**: Bandit security linting
- **Dependencies**: Regular security updates

## Current Development Focus

### Active Epics (August 2025)

#### 1. Data Studio Complete Tool (Epic #65)
**Priority**: High  
**Timeline**: Q4 2025  
**Scope**: 12 tasks including formula engine, export system, NaN handling

#### 2. Session System Unification (Issues #81-85)
**Priority**: Critical  
**Status**: Architecture analysis phase  
**Impact**: Foundation for all data manipulation workflows

#### 3. Celery Async Integration (Issues #54-60)
**Priority**: Medium  
**Status**: Planning phase (6-phase implementation)  
**Scope**: Background processing for ML and data export

### Recently Completed

#### Grove Enhanced Headbar (Issues #39-53)
**Status**: ✅ Complete  
**Achievement**: Two-row navigation with universal search
**Impact**: Modern, professional user interface

#### TanStack Table Implementation 
**Status**: ✅ Complete  
**Achievement**: Modern data grid replacing legacy AG Grid
**Impact**: Improved data manipulation UI

#### Template Rendering Fix (August 24, 2025)
**Status**: ✅ Complete  
**Issue**: Missing `/api/theme/preferences/` endpoint
**Impact**: Restored full application functionality

## Architecture Evolution Plan

### Short Term (Q4 2025)
- ✅ Complete Data Studio implementation
- ✅ Unify session management system
- ✅ Clean up legacy Wave components
- ✅ Optimize base template structure

### Medium Term (Q1-Q2 2026)
- Implement Celery async processing
- Add comprehensive API documentation
- Performance optimization and caching
- Advanced ML experiment features

### Long Term (2026+)
- Microservices architecture consideration
- Advanced analytics and reporting
- Multi-tenant support
- Real-time collaboration features

## Maintenance Guidelines

### Regular Maintenance Tasks
1. **Dependency Updates**: Monthly security and feature updates
2. **Static File Cleanup**: Remove unused CSS/JS files
3. **Database Optimization**: Query performance analysis
4. **Documentation Updates**: Keep architecture docs current
5. **Security Audits**: Regular vulnerability assessments

### Code Review Standards
- All changes must maintain Grove Design System consistency
- Performance impact assessment for data operations
- Security review for user-facing features
- Documentation updates for architectural changes

---

**Maintained By**: Development Team  
**Review Cycle**: Monthly architecture reviews  
**Next Review**: September 2025  
**Related Documents**: All files in `.claude/context/`