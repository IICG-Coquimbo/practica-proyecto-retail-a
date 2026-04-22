# --- SCRAPING TOTTUS DESPENSA (VERSIÓN FINAL LIMPIA) ---
import os
import time
import random
import re
import json
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bson import ObjectId

# --- LIMPIEZA ---
os.system("pkill -9 chrome")
os.system("pkill -9 chromedriver")
print("✅ Entorno limpio.")

# --- VARIABLES ---
NOMBRE_GRUPO = "Vannessa"
CATEGORIA = "Despensa"
URL_TOTTUS = "https://www.tottus.cl/tottus-cl/lista/CATG27055/Despensa"

datos_finales = []
productos_vistos = set()  # 🔥 evita duplicados reales

# --- CONFIG ---
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)

def serializar_datos(lista):
    for item in lista:
        if "_id" in item:
            item["_id"] = str(item["_id"])
    return lista

driver = webdriver.Chrome(options=options)

try:
    print(f"🚀 Cargando {CATEGORIA}...")
    driver.get(URL_TOTTUS)

    print("⏳ Esperando carga inicial...")
    time.sleep(8)

    # --- SCROLL HUMANO ---
    print("🖱️ Scroll humano...")
    for i in range(12):
        driver.execute_script(f"window.scrollBy(0, {random.randint(500,900)});")
        print(f"   Scroll {i+1}")
        time.sleep(random.uniform(1.5, 2.5))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

    # --- EXTRACCIÓN ---
    print("🔍 Escaneando productos...")

    script = """
    let listado = [];
    let todos = document.querySelectorAll('span, div, b, p, strong');

    todos.forEach(el => {
        if (el.innerText.includes('$') && el.innerText.length < 25) {
            let contenedor = el.parentElement;

            for (let i = 0; i < 6; i++) {
                if (contenedor && contenedor.innerText.length > 60) {
                    listado.push(contenedor.innerText);
                    break;
                }
                contenedor = contenedor.parentElement;
            }
        }
    });

    return [...new Set(listado)];
    """

    bloques = driver.execute_script(script)
    print(f"📦 Bloques encontrados: {len(bloques)}")

    # --- FILTRO ---
    palabras_basura = [
        "DESPACHO", "RETIRO", "AGREGAR", "VER MÁS",
        "ORDENAR", "FILTRAR", "CLIENTE", "ENVÍO",
        "PRECIOS", "INCREÍBLES"
    ]

    # --- PROCESAMIENTO ---
    for texto in bloques:
        try:
            lineas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 1]

            precio = next((l for l in lineas if '$' in l), None)

            candidatos = [
                l for l in lineas
                if '$' not in l
                and len(l) > 10
                and not any(p in l.upper() for p in palabras_basura)
            ]

            if precio and candidatos:
                nombre = candidatos[0]

                if len(nombre) < 15 and len(candidatos) > 1:
                    nombre = f"{nombre} {candidatos[1]}"

                # 🔥 eliminar duplicados reales
                if nombre in productos_vistos:
                    continue
                productos_vistos.add(nombre)

                valor_limpio = re.sub(r'[^\d]', '', precio)

                datos_finales.append({
                    "identificador": nombre,
                    "valor": precio,
                    "valor_limpio": float(valor_limpio),
                    "categoria": CATEGORIA,
                    "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "grupo": NOMBRE_GRUPO,
                    "tienda": "Tottus",
                    "url": URL_TOTTUS
                })

                print(f"🛒 [{len(datos_finales)}] {nombre[:50]} | {precio}")

        except:
            continue

finally:
    driver.quit()
    print("\n🛑 Navegador cerrado.")

# --- GUARDADO ---
if datos_finales:

    # Mongo
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        db = client["Canasta_db"]
        coleccion = db["Retail_A"]
        coleccion.insert_many(datos_finales)
        print(f"📦 {len(datos_finales)} guardados en MongoDB.")
    except Exception as e:
        print(f"⚠️ MongoDB error: {e}")

    # JSON
    try:
        with open("tottus_despensa.json", "w", encoding="utf-8") as f:
            json.dump(serializar_datos(datos_finales), f, ensure_ascii=False, indent=2)

        print("💾 Backup creado: tottus_despensa.json")

    except Exception as e:
        print(f"❌ Error JSON: {e}")

else:
    print("❌ No se extrajeron productos.")