# Contenido de scrapers/scraper_soto.py
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- CONSTANTES Y UTILIDADES (Mantener fuera de la función principal) ---
URL_BASE = "https://www.acuenta.cl/ca/despensa/05"
MAX_PAGINAS = 15
NOMBRE_RESPONSABLE = "Jorge Chávez"

CATEGORIAS = {
    'arroz': 'Arroz', 'fideo': 'Pastas', 'pasta': 'Pastas', 'espagueti': 'Pastas', 'tallarines': 'Pastas',
    'aceite': 'Aceites', 'mayonesa': 'Salsas', 'ketchup': 'Salsas', 'salsa': 'Salsas',
    'atún': 'Conservas', 'jurel': 'Conservas', 'azúcar': 'Azúcares', 'harina': 'Harinas', 
    'porotos': 'Legumbres', 'lentejas': 'Legumbres', 'sal': 'Condimentos', 'sopa': 'Instantáneos'
}

def crear_driver():
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def extraer_precio(texto):
    match = re.search(r'\$([0-9]{1,3}(?:\.[0-9]{3})*)', texto)
    if match:
        try: return float(match.group(1).replace('.', ''))
        except: pass
    return 0.0

# --- FUNCIÓN SOLICITADA ---

def ejecutar_extraccion():
    """
    Función principal de extracción para el proyecto de Big Data.
    Retorna una lista de diccionarios con etiquetas estandarizadas.
    """
    # Limpieza inicial
    os.system("pkill -9 chrome")
    os.system("pkill -9 chromedriver")
    
    datos_finales = []
    productos_vistos = set()
    driver = crear_driver()

    try:
        for pagina_actual in range(1, MAX_PAGINAS + 1):
            url = URL_BASE if pagina_actual == 1 else f"{URL_BASE}?currentPage={pagina_actual}"
            driver.get(url)
            time.sleep(8) 

            # Scroll para cargar elementos perezosos (Lazy Load)
            for i in range(10):
                driver.execute_script(f"window.scrollTo(0, {i * 500});")
                time.sleep(0.3)

            bloques = driver.find_elements(By.CSS_SELECTOR, "div[class*='product-card'], .product-item")
            
            for bloque in bloques:
                try:
                    texto = bloque.text.strip()
                    if '$' not in texto: continue
                    
                    precio_val = extraer_precio(texto)
                    lineas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 3]
                    if not lineas: continue
                    
                    nombre_raw = max(lineas, key=len)[:100].strip()
                    id_unico = f"{nombre_raw.lower()}_{int(precio_val)}"

                    if id_unico not in productos_vistos:
                        productos_vistos.add(id_unico)
                        
                        # Mapeo a las etiquetas solicitadas en el ejemplo
                        datos_finales.append({
                            "identificador": nombre_raw,
                            "valor": precio_val,
                            "grupo": "Soto_Team", # Identificador del equipo
                            "metadata": {
                                "responsable": NOMBRE_RESPONSABLE,
                                "supermercado": "ACUENTA",
                                "fecha": time.strftime("%d/%m/%Y")
                            }
                        })
                except:
                    continue
                    
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        driver.quit()

    return datos_finales