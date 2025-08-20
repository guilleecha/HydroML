# HydroML - Advanced Machine Learning Platform

<div align="center">

**A comprehensive, Docker-based machine learning platform for data analysis, experiment management, and model development.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

## Overview

HydroML is a modern, web-based machine learning platform that provides an integrated environment for data scientists and ML engineers. Built with Django and enhanced with cutting-edge web technologies, it offers powerful tools for data exploration, experiment tracking, and model development.

## Features

### Key Highlights
- 🚀 **Fast Setup**: One-command Docker deployment
- 📊 **Interactive Data Studio**: Real-time data exploration with AG Grid
- 🧪 **Experiment Tracking**: Built-in MLflow integration
- 🔄 **Session Management**: Stateful data transformation workflows
- 🎨 **Modern UI**: Responsive design with Tailwind CSS and Alpine.js
- 🔒 **Enterprise Ready**: Comprehensive security and monitoring
- 🐳 **Container Native**: Full Docker and Docker Compose support

### Core Capabilities
- **Multi-format Support**: CSV, Parquet, Excel, and database connections
- **Quality Pipeline**: Automated data quality assessment and reporting
- **Data Fusion**: Advanced tools for combining multiple data sources
- **Hyperparameter Optimization**: Automated parameter tuning with Optuna
- **Model Validation**: Cross-validation and performance metrics
- **Feature Engineering**: Advanced feature transformation tools

## Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hydroML
   ```

2. **Create environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the platform**
   ```bash
   docker-compose up --build
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the platform**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - MLflow UI: http://localhost:5000

For detailed installation instructions, see the [Installation Guide](docs/guides/INSTALLATION_GUIDE.md).

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Django       │    │   Services      │
│                 │    │    Backend      │    │                 │
│ • Tailwind CSS  │◄──►│ • REST APIs     │◄──►│ • PostgreSQL    │
│ • Alpine.js     │    │ • Authentication│    │ • Redis         │
│ • AG Grid       │    │ • Business Logic│    │ • MLflow        │
│ • Plotly.js     │    │ • ORM           │    │ • Celery        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components
- **Core App**: Authentication, navigation, shared utilities
- **Projects App**: Project and data source management
- **Data Tools App**: Data analysis, cleaning, and preparation
- **Experiments App**: ML experiment tracking and management
- **Connectors App**: Database connections and data import
- **Accounts App**: User management and profiles

## Technology Stack

### Backend
- **Framework**: Django 5.2.4
- **Language**: Python 3.11+
- **Database**: PostgreSQL 14
- **Cache/Queue**: Redis 6
- **Task Processing**: Celery
- **ML Tracking**: MLflow 2.22.1

### Frontend
- **CSS Framework**: Tailwind CSS
- **JavaScript**: Alpine.js
- **Data Grid**: AG Grid
- **Visualization**: Plotly.js
- **Build Tools**: npm, PostCSS

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Django Development Server (Gunicorn for production)
- **Process Management**: Celery Workers
- **Monitoring**: Sentry (optional)

## Project Structure

```
hydroML/
├── docs/                    # Documentation
│   ├── guides/             # User guides
│   ├── implementation/     # Technical docs
│   └── archived/           # Historical docs
├── tests/                  # Consolidated test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── management_commands/ # Command tests
├── core/                   # Core Django app
├── projects/               # Project management
├── data_tools/             # Data analysis tools
├── experiments/            # ML experiments
├── connectors/             # Data connections
├── accounts/               # User management
├── static/                 # Static assets
├── media/                  # User uploads
└── docker-compose.yml      # Container orchestration
```

## Documentation

### User Guides
- [Installation Guide](docs/guides/INSTALLATION_GUIDE.md)
- [API Testing Guide](docs/guides/API_TESTING_GUIDE.md)
- [QA Testing Quick Start](docs/guides/QA_TESTING_QUICK_START.md)

### Technical Documentation
- [Technical Overview](docs/TECHNICAL_OVERVIEW.md)
- [Security Audit Report](docs/SECURITY_AUDIT_REPORT.md)
- [Data Studio Implementation](docs/implementation/DATA_STUDIO_IMPLEMENTATION.md)
- [MLflow Integration](docs/implementation/MLFLOW_INTEGRATION_IMPLEMENTATION_SUMMARY.md)

### Development
- [Code Instructions](docs/CLAUDE.md)
- [Refactoring Guide](docs/implementation/REFACTORING_MIGRATION_GUIDE.md)
- [Frontend Modularization](docs/implementation/FRONTEND_MODULARIZATION_COMPLETE.md)

## Development

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd hydroML

# Create virtual environment (recommended: use uv)
uv venv venv
source venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Install frontend dependencies
npm install

# Start development servers
python manage.py runserver
celery -A hydroML worker -l info
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/

# Run with coverage
python -m pytest --cov=.
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 .
pylint *.py

# Type checking
mypy .
```

## Key Features

### Data Studio
Interactive data exploration and cleaning interface with:
- Real-time data grid with AG Grid
- Session-based transformation workflows
- Comprehensive data quality pipeline
- Advanced filtering and sorting capabilities
- Export functionality

### Experiment Management
Complete ML experiment lifecycle with:
- MLflow integration for experiment tracking
- Automated hyperparameter optimization with Optuna
- Model validation and cross-validation
- Performance metrics and analysis
- Experiment comparison and visualization

### Data Integration
Flexible data source management:
- Support for CSV, Parquet, Excel formats
- Database connectivity for external sources
- Data fusion capabilities
- Many-to-many project-datasource relationships
- Quality assessment and validation

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write comprehensive tests
- Document new features
- Follow the existing code patterns

## Security

HydroML takes security seriously. We implement:

- CSRF protection
- XSS filtering
- Secure headers (HSTS, X-Frame-Options)
- Environment-based configuration
- Input validation and sanitization
- Regular dependency updates

For security issues, please email [security@hydroml.com](mailto:security@hydroml.com).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/hydroML/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/hydroML/discussions)
- **Email**: [support@hydroml.com](mailto:support@hydroml.com)

## Acknowledgments

- Django community for the excellent web framework
- MLflow team for experiment tracking capabilities
- AG Grid for the powerful data grid component
- Tailwind CSS for the utility-first CSS framework
- All contributors who have helped improve this project

---

<div align="center">
Made with ❤️ by the HydroML Team
</div>