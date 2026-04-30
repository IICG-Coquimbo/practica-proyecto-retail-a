# --- PASO 0: LIMPIEZA DE PROCESOS ---
import os
import time
import re
import pandas as pd
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Limpieza de infraestructura
os.system("pkill -9 chrome")
os.system("pkill -9 chromedriver")
os.system("rm -rf /tmp/.com.google.Chrome.*")
print("🧹 Motor listo. Iniciando automatización para Unimarc (Categoría: Despensa)...")

# --- VARIABLES GENERALES ---
NOMBRE_GRUPO = "Ave Mayo"
SUPERMERCADO = "Unimarc"
CATEGORIA_OBJETIVO = "Carnes" # <--- Definimos la categoría aquí
URL_BASE_TEMPLATE = "https://www.unimarc.cl/category/carnes?&page="

# URI para MongoDB LOCAL
MONGO_URI_LOCAL = "mongodb://bigdata_mongodb:27017/" 

def limpiar_precio(texto):
    numeros = re.sub(r'[^\d]', '', texto)
    return float(numeros) if numeros else 0.0

def ejecutar_extraccion():
    datos_finales = []
    driver = None
    max_paginas = 32
    limite_max_productos = 1000

    # --- PASO 1: CONFIGURACIÓN DEL NAVEGADOR ---
    options = Options()
    options.binary_location = "/usr/bin/brave-browser" 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        driver = webdriver.Chrome(options=options)
        
        for pagina_actual in range(1, max_paginas + 1):
            if len(datos_finales) >= limite_max_productos:
                print(f"✅ Se alcanzó el límite máximo de {limite_max_productos} productos.")
                break

            url_iterada = f"{URL_BASE_TEMPLATE}{pagina_actual}"
            print(f"\n🌐 Navegando a: {url_iterada}")
            driver.get(url_iterada)
            
            time.sleep(3)

            for s in range(6):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(0.8)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.smu-impressed"))
                )
            except:
                print(f"🏁 No se encontraron más productos en la página {pagina_actual}. Finalizando y guardando...")
                break

            bloques = driver.find_elements(By.CSS_SELECTOR, "section.smu-impressed")
            print(f"📦 Página {pagina_actual}: Detectados {len(bloques)} productos.")

            for bloque in bloques:
                if len(datos_finales) >= limite_max_productos:
                    break
                
                try:
                    marca_txt = bloque.find_element(By.CSS_SELECTOR, "p.Shelf_brandText__vmuWJ").text
                    nombre_txt = bloque.find_element(By.CSS_SELECTOR, "p.Shelf_nameProduct__0KIRG").text
                    precio_txt = bloque.find_element(By.CSS_SELECTOR, "p[id^='listPrice__offerPrice--']").text
                    
                    try:
                        img_url = bloque.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    except:
                        img_url = "URL no encontrada"

                    fecha_actual = time.strftime("%Y-%m-%d %H:%M:%S")

                    datos_finales.append({
                        "fecha_captura": fecha_actual,
                        "nombre_producto": nombre_txt.strip(),
                        "precio": limpiar_precio(precio_txt),
                        "supermercado": SUPERMERCADO,
                        "categoria": CATEGORIA_OBJETIVO, # Etiqueta dinámica
                        "marca": marca_txt.strip().upper(),
                        "imagen": img_url,
                        "responsable": "Renato"
                    })
                except:
                    continue

            print(f"📈 Total acumulado en esta sesión: {len(datos_finales)} productos.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador cerrado.")

    # --- PASO 3: GUARDADO EN MONGODB LOCAL CON PROTECCIÓN DE DATOS ---
    if len(datos_finales) > 0:
        try:
            print(f"\n💾 Conectando a MongoDB LOCAL para guardar {len(datos_finales)} registros...")
            client = MongoClient(MONGO_URI_LOCAL, serverSelectionTimeoutMS=5000)
            db = client["Canasta_db"]
            coleccion = db["Retail_A"] 
            
            # --- CRITICAL: LIMPIEZA ESPECÍFICA ---
            # Solo borramos lo que sea de Renato, en Unimarc Y de la categoría Despensa.
            # Esto deja intactos tus datos de "Carnes".
            filtro_protector = {
                "supermercado": SUPERMERCADO, 
                "responsable": "Renato",
                "categoria": CATEGORIA_OBJETIVO
            }
            coleccion.delete_many(filtro_protector)
            
            coleccion.insert_many(datos_finales, ordered=False)
            print(f"✅ ÉXITO: Los datos de {CATEGORIA_OBJETIVO} se guardaron. 'Carnes' sigue a salvo.")
        except Exception as e:
            print(f"❌ Error al guardar localmente: {e}")

        df = pd.DataFrame(datos_finales)
        print("\n" + "="*130)
        print(df[['nombre_producto', 'precio', 'categoria', 'responsable']].tail(10).to_string(index=False))
        print("="*130)
    else:
        print("⚠️ No se encontró ningún producto para guardar.")

    return datos_finales

if __name__ == "__main__":
    ejecutar_extraccion()