import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

# --- CONFIGURACIÓN ---
NOMBRE_GRUPO = "Ave Mayo"
ENCARGADA = "Isidora Matus"
SUPERMERCADO = "Cugat"
MONGO_URI = "mongodb+srv://FelipeGutierrez:pepe1516@cluster0.6zjv54l.mongodb.net/?appName=Cluster0"

URLS_OBJETIVO = [
    "https://cugat.cl/categoria-producto/despensa/",
    "https://cugat.cl/categoria-producto/carniceria/",
    "https://cugat.cl/categoria-producto/fiambreria-embutidos-y-quesos/",
    "https://cugat.cl/categoria-producto/lacteos/",
    "https://cugat.cl/categoria-producto/bebidas-jugos-y-aguas/" 
]

MARCAS_MAESTRAS = [
    "TUCAPEL", "LUCCHETTI", "CAROZZI", "MAGGI", "LOBOS", "BANQUETE", "CHEF", "NATURA", "MIRAFLORES",
    "BONANZA", "LOS GRANOS", "SANTO TOMAS", "TALLIANI", "ARUNA", "ABRIL", "EDRA", "VIVO", "ZUKO", "LIVEAN",
    "DON JUAN", "HELLMANNS", "HELLMANN´S", "TRAVERSO", "JB", "GOURMET", "KRAFT", "BIOSAL",
    "AGROSUPER", "SUPER POLLO", "SUPER CERDO", "SAN JORGE", "PF", "WINTER", "LA PREFERIDA", "MONTINA", 
    "COLUN", "SOPROLE", "NESTLE", "SURLAT", "CALO", "LONCOLECHE", "QUILLAYES", "COCA COLA", "COCA-COLA", 
    "PEPSI", "FANTA", "SPRITE", "KACHANTUN", "VITAL", "ANDINA", "WATT'S", "WATTS", "PAP", "BILZ", "KEM", 
    "CRUSH", "BENEDICTINOS", "CASA OLIVA", "PURE LIFE", "CANADA DRY", "LIMON SODA", "SEVEN UP"
]

def extraer_precio_real(bloque):
    try:
        precio_tag = bloque.find('bdi')
        if precio_tag:
            nums = "".join(filter(str.isdigit, precio_tag.get_text()))
            return int(nums) if nums else 0
    except: return 0
    return 0

def ejecutar_mega_extraccion():
    datos_finales = []
    vistos = set()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"🚀 Iniciando captura para {ENCARGADA}...")

    for url_seccion in URLS_OBJETIVO:
        try:
            res = requests.get(url_seccion, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            paginas = soup.find_all('a', class_='page-number')
            max_pag = max([int(p.get_text()) for p in paginas if p.get_text().isdigit()]) if paginas else 1
            
            for p in range(1, max_pag + 1):
                response = requests.get(f"{url_seccion}page/{p}/", headers=headers)
                soup_pag = BeautifulSoup(response.text, 'html.parser')
                bloques = soup_pag.find_all('div', class_='product-small')
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for bloque in bloques:
                    name_tag = bloque.find('p', class_='product-title')
                    nombre = " ".join(name_tag.get_text().split()) if name_tag else "N/A"
                    if nombre in vistos or nombre == "N/A": continue
                    vistos.add(nombre)

                    cat_tag = bloque.find('p', class_='product-cat')
                    categoria_limpia = " ".join(cat_tag.get_text().split()) if cat_tag else "Varios"
                    valor_num = extraer_precio_real(bloque)
                    if valor_num == 0 or valor_num > 150000: continue 

                    nombre_up = nombre.upper()
                    marca_encontrada = "OTRA"
                    for m in MARCAS_MAESTRAS:
                        if m in nombre_up:
                            marca_encontrada = m
                            break

                    datos_finales.append({
                        "identificador": nombre, "valor": valor_num, "supermercado": SUPERMERCADO,
                        "categoria": categoria_limpia, "grupo": NOMBRE_GRUPO, "fecha_scraping": fecha_actual,
                        "marca": marca_encontrada, "encargada_scraping": ENCARGADA
                    })
                print(f"📂 Procesando: {url_seccion.split('/')[-2]}... ({len(datos_finales)} items)", end="\r")
        except: continue

    if datos_finales:
        df = pd.DataFrame(datos_finales)
        
        # --- SUBIDA A MONGO ATLAS ---
        try:
            client = MongoClient(MONGO_URI)
            db = client["Canasta_db"]["Retail_A"]
            db.delete_many({"encargada_scraping": ENCARGADA}) 
            db.insert_many(df.to_dict('records'), ordered=False)
            status_mongo = "✅ REGISTRADOS EN MONGO ATLAS"
        except Exception as e:
            status_mongo = f"❌ ERROR ATLAS: {e}"

        # --- REPORTE DETALLADO DE PRODUCTOS ---
        # Configuramos pandas para que no corte las columnas y muestre todo
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.width', 1000)

        print("\n\n" + "═"*100)
        print(f"📋 LISTADO COMPLETO DE PRODUCTOS CAPTURADOS POR: {ENCARGADA}")
        print("═"*100)
        # Imprime solo el Identificador (Nombre), Marca y Valor
        print(df[['identificador', 'marca', 'valor']].to_string(index=False))
        print("═"*100)
        print(f"📊 ESTADO: {status_mongo}")
        print(f"🎯 TOTAL PRODUCTOS: {len(df)}")
        print("═"*100)

if __name__ == "__main__":
    ejecutar_mega_extraccion()