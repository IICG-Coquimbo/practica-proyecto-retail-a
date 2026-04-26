# --- PASO 0: LIMPIEZA DE PROCESOS (Estandarizado) ---
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

# Limpieza para evitar bloqueos en el contenedor 
os.system("pkill -9 chrome")
os.system("pkill -9 chromedriver")
os.system("rm -rf /tmp/.com.google.Chrome.*")
os.system("rm -rf /tmp/.org.chromium.Chromium.*")
print("🧹 Limpieza de procesos completada. Motor listo para Unimarc.")

# --- VARIABLES GENERALES ---
NOMBRE_GRUPO = "Ave Mayo"
SUPERMERCADO = "Unimarc"
URL_BASE = "https://www.unimarc.cl/category/despensa"

# URI de Atlas del grupo
MONGO_URI = "mongodb+srv://FelipeGutierrez:pepe1516@cluster0.6zjv54l.mongodb.net/?appName=Cluster0"

def limpiar_precio(texto):
    """Extrae solo números para el campo 'valor'."""
    numeros = re.sub(r'[^\d]', '', texto)
    return float(numeros) if numeros else 0.0

def ejecutar_extraccion():
    datos_finales = []
    driver = None
    max_paginas = 32

    # --- PASO 1: CONFIGURACIÓN DEL NAVEGADOR ---
    print("🌐 Configurando navegador Brave...")
    options = Options()
    options.binary_location = "/usr/bin/brave-browser" 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(URL_BASE)
        
        print(f"\n🚀 {SUPERMERCADO} iniciado correctamente.")
        print("📺 VE AL VNC (localhost:6080) para configurar la comuna.")
        input("👉 Una vez que veas los productos en el VNC, presiona ENTER aquí para empezar...")

        for pagina_actual in range(1, max_paginas + 1):
            print(f"\n🔍 TRABAJANDO EN PÁGINA {pagina_actual} DE {max_paginas}...")
            
            # Scroll progresivo para cargar imágenes y precios dinámicos
            for s in range(8):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)

            # Espera explícita para asegurar que los productos cargaron en el DOM
            WebDriverWait(driver, 25).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.smu-impressed"))
            )

            bloques = driver.find_elements(By.CSS_SELECTOR, "section.smu-impressed")
            print(f"📦 Se detectaron {len(bloques)} productos en la vista actual.")

            for bloque in bloques:
                try:
                    # Selectores específicos de Unimarc
                    marca_txt = bloque.find_element(By.CSS_SELECTOR, "p.Shelf_brandText__vmuWJ").text
                    nombre_txt = bloque.find_element(By.CSS_SELECTOR, "p.Shelf_nameProduct__0KIRG").text
                    precio_txt = bloque.find_element(By.CSS_SELECTOR, "p[id^='listPrice__offerPrice--']").text
                    fecha_actual = time.strftime("%Y-%m-%d %H:%M:%S")

                    # ESTRUCTURA DE ETIQUETAS SOLICITADA POR EL EQUIPO
                    datos_finales.append({
                        "identificador": nombre_txt.strip(),
                        "valor": limpiar_precio(precio_txt),
                        "fecha_capture": fecha_actual, # Etiqueta común
                        "grupo": NOMBRE_GRUPO,
                        "nombre_producto": nombre_txt.strip(),
                        "precio": limpiar_precio(precio_txt),
                        "supermercado": SUPERMERCADO,
                        "categoria": "Despensa",
                        "marca": marca_txt.strip().upper(),
                        "precio_promedio": 0.0,
                        "fecha_scraping": fecha_actual
                    })
                except Exception as e:
                    # Si falla un producto (ej. sin stock), seguimos con el siguiente
                    continue

            # --- CONTROL DE FLUJO Y SALIDA ANTICIPADA ---
            if pagina_actual < max_paginas:
                print(f"✅ Página {pagina_actual} completada con éxito.")
                print("---------------------------------------------------------")
                print("⌨️  OPCIONES:")
                print("   - Presiona ENTER para ir a la siguiente página.")
                print("   - Escribe 'f' y presiona ENTER para CORTAR AQUÍ y guardar todo.")
                print("---------------------------------------------------------")
                
                decision = input("¿Qué decides? ").lower()
                
                if decision == 'f':
                    print("🛑 Finalización manual activada. Procesando lo capturado...")
                    break
                
                print(f"👉 Por favor, cambia a la página {pagina_actual + 1} en el VNC...")
            else:
                print("🏁 Fin del recorrido: Se alcanzaron las 32 páginas.")

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Sesión de navegador cerrada.")

    # --- PASO 3: GUARDADO EN MONGODB ATLAS Y TABLA DE RESULTADOS ---
    if datos_finales:
        # Carga a la Nube
        try:
            print(f"\n☁️ Conectando a MongoDB Atlas para subir {len(datos_finales)} registros...")
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client["Canasta_db"]
            coleccion = db["Retail_A"]
            
            # Usamos ordered=False para que no se bloquee por duplicados accidentales
            coleccion.insert_many(datos_finales, ordered=False)
            print("✅ Carga exitosa en el Cluster de Felipe.")
        except Exception as e:
            print(f"⚠️ Nota sobre MongoDB: {e}")

        # --- GENERACIÓN DE LA TABLA PANDAS (LO QUE SOLICITASTE) ---
        df = pd.DataFrame(datos_finales)
        
        # Ajustes de visualización para ver TODAS las etiquetas
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.colheader_justify', 'center')
        
        print("\n" + "="*120)
        print(f"📊 TABLA DE DATOS CAPTURADOS - EQUIPO {NOMBRE_GRUPO.upper()}")
        print("="*120)
        
        # Mostramos los últimos 15 productos con todas las etiquetas
        print(df.tail(15).to_string(index=False))
        
        print("="*120)
        print(f"⭐ RESUMEN: {len(df)} ítems procesados con etiquetas estandarizadas.")
        print("="*120)
        
    else:
        print("⚠️ No se capturaron datos. Revisa la conexión o los selectores en el VNC.")
    return datos_finales

# --- INVOCACIÓN DEL SCRIPT (Esto es lo que hace que corra) ---
if __name__ == "__main__":
    ejecutar_extraccion()