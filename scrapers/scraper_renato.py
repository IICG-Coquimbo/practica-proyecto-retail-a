# scrapers/scraper_renato.py
import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- VARIABLES GENERALES ---
SUPERMERCADO = "Unimarc"
CATEGORIA_OBJETIVO = "Despensa" 
URL_BASE_TEMPLATE = "https://www.unimarc.cl/category/despensa?&page="

def limpiar_precio(texto):
    numeros = re.sub(r'[^\d]', '', texto)
    return int(numeros) if numeros else 0

def ejecutar_extraccion():
    print(f"🚀 Iniciando extracción para Renato (Supermercado {SUPERMERCADO})...")
    datos_finales = []
    driver = None
    max_paginas = 30 
    limite_max_productos = 1000

    # --- CONFIGURACIÓN DEL NAVEGADOR (CORREGIDA PARA WINDOWS) ---
    options = Options()
    # Eliminamos binary_location porque usaremos el Chrome de Windows por defecto
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        driver = webdriver.Chrome(options=options)
        
        for pagina_actual in range(1, max_paginas + 1):
            if len(datos_finales) >= limite_max_productos:
                break

            url_iterada = f"{URL_BASE_TEMPLATE}{pagina_actual}"
            print(f"🌐 Navegando a: Página {pagina_actual}")
            driver.get(url_iterada)
            
            time.sleep(3)

            # Scroll para carga de productos
            for s in range(5):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(0.6)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.smu-impressed"))
                )
            except:
                print(f"🏁 Fin de páginas en {pagina_actual}.")
                break

            bloques = driver.find_elements(By.CSS_SELECTOR, "section.smu-impressed")

            for bloque in bloques:
                try:
                    marca_txt = bloque.find_element(By.CSS_SELECTOR, "p.Shelf_brandText__vmuWJ").text
                    nombre_txt = bloque.find_element(By.CSS_SELECTOR, "p.Shelf_nameProduct__0KIRG").text
                    precio_txt = bloque.find_element(By.CSS_SELECTOR, "p[id^='listPrice__offerPrice--']").text
                    
                    try:
                        img_url = bloque.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    except:
                        img_url = "URL no encontrada"

                    # 🔥 FORMATO SOLICITADO PARA EL MAIN.PY
                    datos_finales.append({
                        "nombre_producto": nombre_txt.strip(),
                        "precio": limpiar_precio(precio_txt),
                        "fecha_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "supermercado": SUPERMERCADO,
                        "categoria": CATEGORIA_OBJETIVO,
                        "marca": marca_txt.strip().upper() if marca_txt else "NO ESPECIFICADA",
                        "imagen": img_url,
                        "responsable": "Renato"
                    })
                except:
                    continue

            print(f"📈 Acumulado: {len(datos_finales)} productos.", end="\r")

    except Exception as e:
        print(f"\n❌ Error en scraper de Renato: {e}")
    finally:
        if driver:
            driver.quit()

    print(f"\n✅ Extracción de Renato finalizada. {len(datos_finales)} productos.")
    return datos_finales

if __name__ == "__main__":
    ejecutar_extraccion()