# 1. Usar una imagen base oficial de Python (versión actualizada)
FROM python:3.11-slim

# 2. Variables de entorno recomendadas
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar dependencias
# Se copia solo requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del proyecto al contenedor
COPY . .