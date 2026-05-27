<<<<<<< HEAD
# Imagen base: trae Jupyter + Python + PySpark ya configurado
=======
# Imagen base con Jupyter + PySpark
>>>>>>> cbbf5e26c966b069a9dc2e730d2a594d9b9ee31f
FROM jupyter/pyspark-notebook:latest

# Cambia al usuario administrador (root) para poder instalar programas
USER root

<<<<<<< HEAD
# 1. Actualiza repositorios e instala herramientas básicas, instala Google Chrome y librerías necesarias
=======
# Instala entorno visual, supervisor y Chrome
>>>>>>> cbbf5e26c966b069a9dc2e730d2a594d9b9ee31f
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
<<<<<<< HEAD
    ca-certificates && \
    mkdir -p /etc/apt/keyrings && \
    wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y \
    google-chrome-stable \
    libnss3 \
    libgbm1 \
    libasound2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# 2. Instala librerías de Python necesarias
RUN pip install selenium pymongo webdriver-manager

# Vuelve al usuario normal de Jupyter (buena práctica de seguridad)
USER jovyan
=======
    ca-certificates \
    openssl \
    xvfb \
    fluxbox \
    x11vnc \
    supervisor \
    python3-websockify \
    novnc \
    libnss3 \
    libgbm1 \
    libasound2 \
    sed \
    && mkdir -p /etc/apt/keyrings \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. InstalaciÃ³n de JARs: VersiÃ³n 10.3.0 (Compatible con Spark 3.5)
# Limpiamos la carpeta primero para que no queden versiones viejas chocando
RUN rm -f /usr/local/spark/jars/mongo-spark-connector* && \
    rm -f /usr/local/spark/jars/mongodb-driver* && \
    rm -f /usr/local/spark/jars/bson*
    
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/bson-record-codec/4.11.1/bson-record-codec-4.11.1.jar -P /usr/local/spark/jars/

# 3. Librerï¿½as de Python para todo el curso (Scraping + Atlas + Spark)
RUN pip install --no-cache-dir --upgrade pip && \
    #pip install --no-cache-dir "pymongo[srv]" dnspython certifi selenium webdriver-manager pandas
    pip install --no-cache-dir "pymongo[srv]" dnspython selenium webdriver-manager pandas certifi


    

# Variables del entorno grÃ¡fico
ENV DISPLAY=:99
ENV SCREEN_WIDTH=1368
ENV SCREEN_HEIGHT=768
ENV SCREEN_DEPTH=24

# Copia archivos de inicio
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Convierte saltos de lÃ­nea Windows a Linux y da permisos
RUN sed -i 's/\r$//' /usr/local/bin/start-vnc.sh && chmod +x /usr/local/bin/start-vnc.sh

# Puertos del contenedor
EXPOSE 8888 5900 6080 4040

# Inicia supervisord
# Iniciamos como root para evitar el error de setuid de la sesiÃ³n anterior
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
>>>>>>> cbbf5e26c966b069a9dc2e730d2a594d9b9ee31f
