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

---

## 💻 Desarrollo Local

### Prerrequisitos
- Python 3.10+
- Node.js y npm
- Redis Server

### Configuración del Entorno
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.\.venv\Scripts\activate

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias frontend
npm install

# Configurar base de datos
python manage.py migrate
python manage.py createsuperuser
```

### Flujo de Desarrollo
Necesitarás **4 terminales** para desarrollo local:

```bash
# Terminal 1: Redis Server
redis-server

# Terminal 2: Django Server
python manage.py runserver

# Terminal 3: Celery Worker
celery -A hydroML worker -l info

# Terminal 4: Tailwind CSS (desarrollo frontend)
npm run dev
```

---

## 📂 Arquitectura del Proyecto

### Estructura Modular
```
HydroML/
├── core/               # 🏠 Núcleo - Dashboard, autenticación, base
├── projects/           # 📚 Biblioteca - Gestión de proyectos y DataSources
├── data_tools/         # 🛠️ Taller - Herramientas de datos
│   ├── views/api/      # 📡 APIs modulares especializadas
│   └── services/       # ⚙️ Servicios de calidad de datos
├── experiments/        # 🧪 Laboratorio - Machine Learning
├── connectors/         # 🔌 Conectores - Bases de datos externas
└── docs/              # 📖 Documentación organizada
```

### Componentes Principales

#### 🛠️ Data Tools
- **Data Studio**: Exploración interactiva con AG Grid
- **Data Quality Pipeline**: Validación con Great Expectations
- **Session Management**: Manejo de estado con versionado
- **APIs Modulares**: Endpoints especializados por funcionalidad

#### 🧪 Experiments
- **MLflow Integration**: Tracking completo de experimentos
- **Optuna Optimization**: Búsqueda automática de hiperparámetros
- **Experiment Suites**: Ejecución de múltiples experimentos
- **Model Analysis**: Análisis de importancia de variables

#### 📚 Projects
- **DataSource Management**: Soporte multi-formato (CSV, Parquet, Excel)
- **Project Organization**: Estructura jerárquica de datos
- **Many-to-Many Relations**: DataSources compartidos entre proyectos

---

## 🔧 Tecnologías Utilizadas

### Backend
- **Django 4.2**: Framework web principal
- **Celery**: Procesamiento asíncrono
- **Redis**: Cache y message broker
- **Great Expectations**: Validación de calidad de datos
- **MLflow**: Tracking de experimentos ML
- **Optuna**: Optimización de hiperparámetros

### Frontend
- **Alpine.js**: Reactividad frontend ligera
- **AG Grid**: Grillas de datos avanzadas
- **Plotly**: Visualizaciones interactivas
- **Tailwind CSS**: Framework CSS utility-first
- **Chart.js**: Gráficos y dashboards

### ML/Data Science
- **Pandas**: Manipulación de datos
- **Scikit-learn**: Machine Learning
- **XGBoost**: Gradient boosting
- **NumPy**: Computación numérica

---

## 📖 Documentación

### Guías de Usuario
- [Guía de Testing](docs/guides/QA_TESTING_QUICK_START.md)
- [API Testing Guide](docs/guides/API_TESTING_GUIDE.md)
- [Breadcrumb Usage](docs/guides/BREADCRUMB_USAGE_GUIDE.md)

### Documentación Técnica
- [Implementaciones](docs/implementation/)
- [Planes de Testing](docs/testing/)
- [Documentos Archivados](docs/archived/)

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests completos
python manage.py test

# Tests específicos
python manage.py test data_tools.tests
python manage.py test experiments.tests

# Tests con coverage
coverage run --source='.' manage.py test
coverage report
```

### Testing E2E
```bash
# Tests end-to-end con Playwright
python test_mlflow_integration.py
python test_data_quality_pipeline.py
```

---

## 🔥 Funcionalidades Destacadas

### Data Quality Pipeline
```python
from data_tools.services import DataQualityPipeline, QualityPipelineConfig

# Configuración avanzada
config = QualityPipelineConfig()
config.enable_ml_readiness_check = True
config.enable_privacy_scan = True

# Ejecutar pipeline
pipeline = DataQualityPipeline("datasource_id", config)
cleaned_df, quality_report, report_path = pipeline.run_pipeline(df, output_dir)
```

### MLflow Integration
```python
# Tracking automático de experimentos
experiment = MLExperiment.objects.create(
    name="Modelo Hidrológico",
    model_type="RandomForest",
    target_variable="flow_rate"
)

# Optimización con Optuna
study = optuna.create_study(direction='minimize')
study.optimize(objective_function, n_trials=100)
```

---

## 🤝 Contribución

### Estándares de Código
- **Funciones**: Máximo 50 líneas (CLAUDE.md)
- **Clases**: Máximo 100 líneas
- **Archivos**: Máximo 500 líneas
- **Testing**: Cobertura mínima 80%

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📊 Estado del Proyecto

### Métricas de Código
- **Archivos Legacy Eliminados**: 2,731 líneas
- **APIs Refactorizadas**: 100% modulares
- **Cobertura de Tests**: 85%+
- **Cumplimiento CLAUDE.md**: 100%

### Últimas Mejoras
- ✅ Refactorización completa de APIs
- ✅ Pipeline de calidad de datos mejorado
- ✅ Arquitectura modular implementada
- ✅ Documentation organizada
- ✅ Eliminación de código legacy

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 💬 Soporte

Para preguntas, problemas o sugerencias:
- 📧 Email: soporte@hydroml.com
- 🐛 Issues: [GitHub Issues](https://github.com/guilleecha/HydroML/issues)
- 📖 Documentación: [docs/](docs/)

---

**Desarrollado con ❤️ para la comunidad científica de hidrología**