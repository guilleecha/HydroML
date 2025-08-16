# 1. Usar una imagen base oficial de Python (versión actualizada)
FROM python:3.11-slim

# 2. Variables de entorno recomendadas
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Instalar dependencias del sistema para WeasyPrint y otras librerías
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgdk-pixbuf-2.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libfontconfig1 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-dev \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 5. Instalar dependencias de Python
# Se copia solo requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del código del proyecto al contenedor
COPY . .