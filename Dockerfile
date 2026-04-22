<<<<<<< HEAD
<<<<<<< HEAD
=======
# Imagen base con Jupyter + PySpark (Spark 3.5.x)
>>>>>>> 69d3a111fab055141859cae0becfe7f5e0d88254
=======
>>>>>>> 847d964ca522bae566d49d84acff60a9bc264f0c
FROM jupyter/pyspark-notebook:latest

USER root

<<<<<<< HEAD
<<<<<<< HEAD
# 1. Instalar dependencias base y configurar el repo de Google Chrome
# Nota: Se han unido las lÃ­neas con \ correctamente
RUN apt-get update && apt-get install -y wget gnupg2 curl && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# 2. Instalar Google Chrome y librerÃ­as de soporte
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    libnss3 \
    libgbm1 \
    libasound2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Instalar librerÃ­as de Python
RUN pip install selenium pymongo webdriver-manager

USER jovyan
# Imagen base: trae Jupyter + Python + PySpark ya configurado
FROM jupyter/pyspark-notebook:latest

# Cambia al usuario administrador (root) para poder instalar programas
USER root

# 1. Actualiza repositorios e instala herramientas b sicas, instala Google Chrome y librer as necesarias
=======
# 1. Instalación de dependencias del sistema y entorno visual
>>>>>>> 69d3a111fab055141859cae0becfe7f5e0d88254
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
# 2. Instala librer as de Python necesarias
RUN pip install selenium pymongo webdriver-manager

# Vuelve al usuario normal de Jupyter (buena pr ctica de seguridad)
USER jovyan
=======
=======
# 1. Herramientas de Red, SSL y Entorno Gráfico (Xvfb para el scraper)
RUN apt-get update && apt-get install -y \
>>>>>>> 847d964ca522bae566d49d84acff60a9bc264f0c
    ca-certificates \
    openssl \
    curl \
    xvfb \
    fluxbox \
    x11vnc \
    supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Instalamos Brave Browser (o Chromium) para el scraping
RUN curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list \
    && apt-get update && apt-get install -y brave-browser

# 3. Librerías de Python para todo el curso (Scraping + Atlas + Spark)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "pymongo[srv]" dnspython certifi selenium webdriver-manager pandas

# 4. Conectores Spark-MongoDB
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar -P /usr/local/spark/jars/

# 5. Configuración de visualización (noVNC)
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod +x /usr/local/bin/start-vnc.sh

<<<<<<< HEAD
RUN sed -i 's/\r$//' /usr/local/bin/start-vnc.sh \
    && chmod +x /usr/local/bin/start-vnc.sh && \
    chown -R jovyan:users /home/jovyan/work

EXPOSE 8888 5900 6080 4040

# Iniciamos como root para evitar el error de setuid de la sesión anterior
USER root
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
>>>>>>> 69d3a111fab055141859cae0becfe7f5e0d88254
=======
ENV DISPLAY=:99
# Supervisor lanza Jupyter y el Entorno Gráfico al mismo tiempo
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
>>>>>>> 847d964ca522bae566d49d84acff60a9bc264f0c
