# --- PASO 0: LIMPIEZA DE PROCESOS (Estandarizado) ---
import os
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

# Limpieza para evitar conflictos en el entorno de ejecución
os.system("pkill -9 chrome")
os.system("pkill -9 chromedriver")
os.system("rm -rf /tmp/.com.google.Chrome.*")
os.system("rm -rf /tmp/.org.chromium.Chromium.*")
print("🧹 Limpieza de procesos completada. Motor listo para Cugat.")

# --- VARIABLES GENERALES (Alineadas con el Cluster de Felipe) ---
NOMBRE_GRUPO = "Ave Mayo"
ENCARGADA = "Isidora Matus"
SUPERMERCADO = "Cugat"
URL_BASE = "https://cugat.cl/categoria-producto/despensa/"

# URI de Atlas del grupo (Cluster de Felipe)
MONGO_URI = "mongodb+srv://FelipeGutierrez:pepe1516@cluster0.6zjv54l.mongodb.net/?appName=Cluster0"

# Diccionario de marcas para estandarización de datos
MARCAS_CONOCIDAS = [
    "LINDEROS", "TUCAPEL", "MARIPOSA", "OTUNA", "ARUNA", "LOS GRANOS", "MAGGI", 
    "DON JUAN", "TRAVERSO", "ESMERALDA", "LOBOS", "MIRAFLORES", "HELLMANNS", 
    "HELLMANN´S", "BONANZA", "PARRAL", "YBARRA", "COLISEO", "ROMANO", "MAKAROMA", 
    "WASIL", "EL MONTE", "TALLIANI", "LUCCHETTI", "ASTRA", "NATUREZZA", "SANTO TOMAS", 
    "PASTANOVA", "MALLOA", "BANQUETE", "KRAFT", "MONT BLANC", "CISNE", "VAN CAMP´S", 
    "VAN CAMP’S", "LOS CHINOS", "ABRIL", "COPIHUE", "LOS ANDES", "ALUFOIL", "ALUPLAST", 
    "CAROZZI", "SAN JOSE", "TOSCANA", "GOURMET", "PERFECT CHOICE", "SELECTA", 
    "IMPERIAL", "ACONCAGUA", "EDRA", "NATURA", "MAIZENA", "DROPA", "LEFERSA", 
    "COLLICO", "AMBROSOLI", "VIVO", "DOS CABALLOS", "ROBINSON CRUSOE", "BIOSAL", 
    "JB", "CHEF"
]

def extraer_marca(nombre_completo):
    """Lógica para identificar la marca dentro del nombre del producto."""
    nombre_upper = nombre_completo.upper()
    for marca in MARCAS_CONOCIDAS:
        if marca in nombre_upper:
            return marca
    return nombre_upper.split()[0].replace(',', '').strip()

def ejecutar_extraccion():
    datos_finales = []
    vistos = set()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    print(f"🚀 Iniciando extracción de {SUPERMERCADO} para el equipo {NOMBRE_GRUPO}...")

    try:
        # Detectar cantidad de páginas dinámicamente
        res = requests.get(URL_BASE, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        paginas_tags = soup.find_all('a', class_='page-number')
        max_paginas = max([int(p.get_text()) for p in paginas_tags if p.get_text().isdigit()]) if paginas_tags else 1
        
        for pagina_actual in range(1, max_paginas + 1):
            print(f"🔍 PROCESANDO PÁGINA {pagina_actual} DE {max_paginas}...", end="\r")
            
            url_pag = f"{URL_BASE}page/{pagina_actual}/"
            response = requests.get(url_pag, headers=headers)
            soup_pag = BeautifulSoup(response.text, 'html.parser')
            bloques = soup_pag.find_all('div', class_='product-small')

            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for bloque in bloques:
                try:
                    name_tag = bloque.find('p', class_='product-title')
                    nombre_raw = name_tag.get_text().strip() if name_tag else "N/A"
                    nombre_limpio = " ".join(nombre_raw.split())
                    
                    if nombre_limpio in vistos or nombre_limpio == "N/A": continue
                    vistos.add(nombre_limpio)

                    # Procesamiento de Marca y Precio
                    marca_txt = extraer_marca(nombre_limpio)
                    price_wrapper = bloque.find('span', class_='price')
                    precio_num = 0
                    if price_wrapper:
                        ins_tag = price_wrapper.find('ins')
                        price_text = ins_tag.get_text() if ins_tag else price_wrapper.get_text()
                        precio_num = int("".join(filter(str.isdigit, price_text.split('$')[-1])))

                    # ESTRUCTURA DE ETIQUETAS ESTANDARIZADA (Alineada con el equipo)
                    datos_finales.append({
                        "identificador": nombre_limpio,
                        "valor": float(precio_num),
                        "fecha_capture": fecha_actual,
                        "grupo": NOMBRE_GRUPO,
                        "encargada_scraping": ENCARGADA,
                        "nombre_producto": nombre_limpio,
                        "precio": float(precio_num),
                        "supermercado": SUPERMERCADO,
                        "categoria": "Despensa",
                        "marca": marca_txt,
                        "precio_promedio": 0.0,  # Se actualiza al final
                        "fecha_scraping": fecha_actual
                    })
                except:
                    continue
            
            time.sleep(0.3)

    except Exception as e:
        print(f"❌ Error durante la extracción: {e}")

    # --- GUARDADO EN MONGODB ATLAS Y VISUALIZACIÓN ---
    if datos_finales:
        # Calcular precio promedio antes de subir
        df_final = pd.DataFrame(datos_finales)
        promedio_val = df_final[df_final['valor'] > 0]['valor'].mean()
        for item in datos_finales: 
            item["precio_promedio"] = round(float(promedio_val), 2)

        try:
            print(f"\n☁️ Subiendo {len(datos_finales)} registros al Cluster de Felipe...")
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client["Canasta_db"]
            coleccion = db["Retail_A"]
            
            # Insertar datos evitando bloqueos
            coleccion.insert_many(datos_finales, ordered=False)
            print("✅ Sincronización exitosa con MongoDB Atlas.")
        except Exception as e:
            print(f"⚠️ Nota sobre la base de datos: {e}")

        # Configuración de salida en consola (Pandas)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        
        print("\n" + "="*120)
        print(f"📊 REPORTE DE CAPTURA - {ENCARGADA.upper()} | EQUIPO: {NOMBRE_GRUPO}")
        print("="*120)
        print(df_final.tail(15).to_string(index=False))
        print("="*120)
        print(f"⭐ RESUMEN: {len(df_final)} productos | Promedio: ${promedio_val:,.0f}".replace(',', '.'))
        
    else:
        print("⚠️ No se obtuvieron datos para procesar.")
    
    return datos_finales

if __name__ == "__main__":
    ejecutar_extraccion()