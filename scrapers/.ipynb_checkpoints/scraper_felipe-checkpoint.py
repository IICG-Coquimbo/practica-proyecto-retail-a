import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ejecutar_extraccion():
    """
    Función estandarizada para el Orquestador (main.py).
    Realiza el scraping de ServiChop e integra etiquetas personalizadas.
    """
    # --- CONFIGURACIÓN DEL NAVEGADOR ---
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    datos_finales = []
    driver = None

    try:
        driver = webdriver.Chrome(options=options)
        limite_paginas = 5
        driver.get("https://www.serviceshop.cl/llena-tu-despensa")

        for nivel_pagina in range(limite_paginas):
            # Tiempo de espera para carga de elementos dinámicos
            time.sleep(10) 
            
            # Espera explícita a que aparezcan los bloques de productos
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-block"))
            )

            bloques = driver.find_elements(By.CSS_SELECTOR, ".product-block")

            for bloque in bloques:
                try:
                    # Extracción de datos básicos
                    nombre_raw = bloque.find_element(By.TAG_NAME, "h3").text
                    precio_raw = bloque.find_element(By.CSS_SELECTOR, ".price").text
                    fecha_ahora = time.strftime("%Y-%m-%d %H:%M:%S")

                    # Limpieza del precio para que sea numérico (estándar de calidad)
                    precio_limpio = precio_raw.replace(".", "").replace("$", "").replace(",", "").strip()
                    precio_numerico = float(precio_limpio) if precio_limpio.isdigit() else 0.0

                    # --- CONSTRUCCIÓN DEL DICCIONARIO CON TODAS LAS ETIQUETAS ---
                    datos_finales.append({
                        # 1. Campos obligatorios
                        "identificador": nombre_raw,
                        "valor": precio_numerico,
                        "fecha_captura": fecha_ahora,
                        "grupo": "Ave Mayo",

                        # 2. Etiquetas adicionales solicitadas
                        "nombre_producto": nombre_raw,
                        "precio": precio_numerico,
                        "supermercado": "ServiChop",
                        "categoria": "Despensa",
                        "marca": "No especificada",
                        "precio_promedio": 0.0,
                        "fecha_scraping": fecha_ahora
                    })
                except Exception as e:
                    # Si falla un producto, continúa con el siguiente
                    continue

            # --- LÓGICA DE PAGINACIÓN ---
            try:
                btn_sig = driver.find_element(By.CLASS_NAME, "s-pagination-next")
                driver.execute_script("arguments[0].click();", btn_sig)
            except:
                # Si no hay más páginas, rompe el ciclo
                break

    except Exception as e:
        print(f"Error crítico en la extracción de Felipe: {e}")
    
    finally:
        if driver:
            driver.quit()

    return datos_finales