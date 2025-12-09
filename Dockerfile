# Dockerfile para Sistema de Transformación de Guaraní
FROM python:3.11-slim

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app.py .
COPY .env .env

# Copiar vector store ACTUALIZADO (faiss_store)
COPY faiss_store/ ./faiss_store/

# Exponer puerto de Gradio
EXPOSE 7860

# Variables de entorno
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV GRADIO_ANALYTICS_ENABLED=false

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
