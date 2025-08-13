# HydroML 💧

HydroML es una plataforma web construida con Django para el análisis interactivo, la preparación y el modelado de datos hidrológicos mediante técnicas de Machine Learning.

---
## 🚀 Requisitos Previos

Asegúrate de tener instalado el siguiente software en tu sistema:
* [Git](https://git-scm.com/)
* [Python 3.10+](https://www.python.org/)
* [Node.js y npm](https://nodejs.org/)
* [WSL (Subsistema de Windows para Linux)](https://learn.microsoft.com/es-es/windows/wsl/install)
* **Redis** (instalado dentro de tu WSL). Si no lo tienes, ábrelo y ejecuta:
    ```bash
    sudo apt-get update && sudo apt-get install redis-server
    ```

---
## 🛠️ Configuración Inicial del Proyecto

Sigue estos pasos la primera vez que configures el proyecto en un nuevo ordenador.

### 1. Clonar el Repositorio
```bash
git clone [https://github.com/guilleecha/HydroML.git](https://github.com/guilleecha/HydroML.git)
cd HydroML
 ```

### 2. Crear y Activar el Entorno Virtual de Python
```bash
# Instalar paquetes de Python
pip install -r requirements.txt

# Instalar paquetes de Node.js para el frontend
npm install
 ```

### 3. Instalar Dependencias
```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno en PowerShell
.\.venv\Scripts\activate
 ```

### 4. Configurar la Base de Datos

```bash
# Aplicar las migraciones a la base de datos
python manage.py migrate

# Crear tu usuario administrador
python manage.py createsuperuser
 ```




## 💻 Flujo de Trabajo de Desarrollo

Para correr la aplicación en modo de desarrollo, necesitarás tener **cuatro terminales abiertas** ejecutando los siguientes procesos simultáneamente.

### Terminal 1: Servidor de Redis (en WSL)
Este proceso actúa como el intermediario para las tareas en segundo plano.
```bash
# 1. Abre la terminal de WSL (escribe 'wsl' en el menú de inicio)
wsl

# 2. Inicia el servidor de Redis
redis-server
```

---
## 📂 Arquitectura del Proyecto

El proyecto está organizado en una arquitectura modular para facilitar su mantenimiento y escalabilidad:

* **`core`**: Gestiona la lógica principal del sitio, plantillas base (`base.html`) y la página de inicio.
* **`projects`**: La "Biblioteca" 📚. Responsable de gestionar los proyectos y los `DataSources`.
* **`data_tools`**: El "Taller" 🛠️. Contiene todas las herramientas para procesar y manipular datos (Visor, Preparador, Fusor).
* **`experiments`**: El "Laboratorio" 🧪. Dedicado exclusivamente a la gestión y ejecución de experimentos de Machine Learning.

---

## Importancia de Variables

Esta funcionalidad permite calcular y visualizar la importancia de las variables de un modelo de Machine Learning entrenado. 

### Cómo usar:
1. Asegúrate de que el experimento esté en estado `FINISHED`.
2. Haz clic en el botón "Analizar Modelo" en la página de detalles del experimento.
3. Una vez completado el análisis, se mostrará un gráfico de barras con la importancia de las variables.

### Tecnologías utilizadas:
- **Celery**: Para ejecutar el cálculo de forma asíncrona.
- **Chart.js**: Para visualizar la importancia de las variables.