# HydroML Installation Guide

## Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository
- **Node.js**: Version 16+ (for frontend dependencies)

### Supported Operating Systems
- Windows 10/11 (with WSL2 recommended)
- macOS 10.15+
- Ubuntu 20.04+ / Debian 11+
- CentOS 8+ / RHEL 8+

## Quick Start with Docker (Recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hydroML
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```bash
# Django Configuration
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration
POSTGRES_NAME=hydro_db
POSTGRES_USER=hydro_user
POSTGRES_PASSWORD=hydro_pass
POSTGRES_HOST=db

# Redis Configuration
REDIS_HOST=redis

# MLflow Configuration
MLFLOW_TRACKING_URI=http://mlflow:5000

# Sentry Configuration (Optional)
SENTRY_DSN=your-sentry-dsn-here
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0

# Security (Production)
SECURE_SSL_REDIRECT=False
DJANGO_FERNET_KEY=your-fernet-key-here
```

### 3. Build and Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Database Setup
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec web python manage.py seeddb
```

### 5. Access the Application
- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **MLflow UI**: http://localhost:5000

## Development Installation

### 1. Python Environment Setup
```bash
# Create virtual environment (recommended: use uv)
uv venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Frontend Dependencies
```bash
# Install Node.js dependencies
npm install

# Build CSS (Tailwind)
npm run build

# Watch for changes (development)
npm run dev
```

### 3. Database Setup (Local PostgreSQL)
```bash
# Install PostgreSQL locally
# Create database and user
createdb hydro_db
createuser hydro_user

# Update .env file with local database settings
POSTGRES_HOST=localhost
```

### 4. Start Development Server
```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A hydroML worker -l info

# Start Redis (if not using Docker)
redis-server
```

## Production Deployment

### 1. Environment Configuration
Update `.env` file for production:
```bash
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
```

### 2. Security Considerations
- Generate secure SECRET_KEY and FERNET_KEY
- Configure proper HTTPS termination
- Set up regular database backups
- Configure monitoring and alerting
- Update ALLOWED_HOSTS appropriately

### 3. Performance Optimization
- Use PostgreSQL with proper indexing
- Configure Redis for production
- Set up CDN for static files
- Enable gzip compression
- Configure proper logging

## Troubleshooting

### Common Issues

#### Docker Permission Issues
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

#### Port Conflicts
```bash
# Check which process is using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up --build
```

#### Memory Issues
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs worker
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f web
```

## Testing

### Run Test Suite
```bash
# Run all tests
docker-compose exec web python -m pytest

# Run specific test categories
docker-compose exec web python -m pytest tests/unit/
docker-compose exec web python -m pytest tests/integration/
docker-compose exec web python -m pytest tests/e2e/

# Run with coverage
docker-compose exec web python -m pytest --cov=.
```

### Quality Assurance
```bash
# Run management commands for QA
docker-compose exec web python manage.py check
docker-compose exec web python manage.py validate_templates
```

## Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
uv pip install -r requirements.txt

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup and Restore
```bash
# Database backup
docker-compose exec db pg_dump -U hydro_user hydro_db > backup.sql

# Database restore
docker-compose exec -T db psql -U hydro_user hydro_db < backup.sql
```

## Support

For additional support:
1. Check the [Technical Overview](../TECHNICAL_OVERVIEW.md)
2. Review existing [documentation](../README.md)
3. Check the [troubleshooting section](#troubleshooting)
4. Create an issue in the project repository