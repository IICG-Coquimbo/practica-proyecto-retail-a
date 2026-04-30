import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
from pymongo import MongoClient

# --- CONFIGURACIÓN ---
MONGO_URI = "mongodb://database:27017/" 
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ENCARGADA = "Isidora Matus"
SUPERMERCADO = "Cugat"

URLS_OBJETIVO = [
    "https://cugat.cl/categoria-producto/despensa/",
    "https://cugat.cl/categoria-producto/carniceria/",
    "https://cugat.cl/categoria-producto/fiambreria-embutidos-y-quesos/",
    "https://cugat.cl/categoria-producto/lacteos/",
    "https://cugat.cl/categoria-producto/bebidas-jugos-y-aguas/"
]

# Lista extendida para minimizar los "OTRA"
MARCAS_MAESTRAS = [
    "TUCAPEL", "LUCCHETTI", "CAROZZI", "MAGGI", "LOBOS", "BANQUETE", "CHEF", "NATURA", "MIRAFLORES",
    "BONANZA", "LOS GRANOS", "SANTO TOMAS", "TALLIANI", "ARUNA", "ABRIL", "EDRA", "VIVO", "ZUKO", "LIVEAN",
    "DON JUAN", "HELLMANNS", "HELLMANN´S", "TRAVERSO", "JB", "GOURMET", "KRAFT", "BIOSAL", "AGROSUPER", 
    "SUPER POLLO", "SUPER CERDO", "SAN JORGE", "PF", "WINTER", "LA PREFERIDA", "MONTINA", "COLUN", 
    "SOPROLE", "NESTLE", "SURLAT", "CALO", "LONCOLECHE", "QUILLAYES", "COCA COLA", "COCA-COLA", "PEPSI", 
    "FANTA", "SPRITE", "KACHANTUN", "VITAL", "ANDINA", "WATT'S", "WATTS", "PAP", "BILZ", "KEM", "CRUSH", 
    "BENEDICTINOS", "CASA OLIVA", "PURE LIFE", "CANADA DRY", "LIMON SODA", "SEVEN UP",
    "LINDEROS", "MARIPOSA", "OTUNA", "COPITA", "YANINE", "COPIHUE", "ESMERALDA", "YBARRA", "COLISEO", 
    "ROMANO", "MAKAROMA", "PASTANOVA", "WASIL", "EL MONTE", "ASTRA", "NATUREZZA", "MALLOA", "MONT BLANC", 
    "CISNE", "VAN CAMP", "VAN CAMP´S", "LOS CHINOS", "PARRAL", "DON VITTORIO"
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
    print(f"🚀 Iniciando extracción para {ENCARGADA}...")
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        db = client["Canasta_db"]
        collection = db["Retail_A"]
        client.server_info()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return

    datos_finales = []
    vistos = set()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for url_base in URLS_OBJETIVO:
        try:
            res = requests.get(url_base, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            paginas = soup.find_all('a', class_='page-number')
            max_pag = max([int(p.get_text()) for p in paginas if p.get_text().isdigit()]) if paginas else 1
            
            for p in range(1, max_pag + 1):
                url_pag = f"{url_base}page/{p}/"
                response = requests.get(url_pag, headers=HEADERS)
                soup_pag = BeautifulSoup(response.text, 'html.parser')
                bloques = soup_pag.find_all('div', class_='product-small')

                for bloque in bloques:
                    name_tag = bloque.find('p', class_='product-title')
                    nombre = " ".join(name_tag.get_text().split()) if name_tag else "N/A"
                    if nombre in vistos or nombre == "N/A": continue
                    vistos.add(nombre)

                    img_tag = bloque.find('img')
                    url_imagen = img_tag.get('src') if img_tag else "N/A"

                    # Lógica de Marca
                    nombre_up = nombre.upper()
                    marca_encontrada = "OTRA"
                    for m in MARCAS_MAESTRAS:
                        if m in nombre_up:
                            marca_encontrada = m
                            break

                    precio_num = extraer_precio_real(bloque)
                    if precio_num == 0: continue 

                    cat_tag = bloque.find('p', class_='product-cat')
                    categoria_limpia = " ".join(cat_tag.get_text().split()) if cat_tag else "Varios"

                    # Ajuste solicitado: nombre_producto y precio
                    datos_finales.append({
                        "nombre_producto": nombre, 
                        "precio": precio_num, 
                        "supermercado": SUPERMERCADO,
                        "categoria": categoria_limpia, 
                        "fecha_captura": fecha_actual, 
                        "marca": marca_encontrada, 
                        "responsable": ENCARGADA,
                        "imagen": url_imagen 
                    })
                print(f"📂 Procesando: {url_base.split('/')[-2]} Pág {p}...", end="\r")
        except: continue

    if datos_finales:
        # Limpieza por responsable
        collection.delete_many({"responsable": ENCARGADA})
        collection.insert_many(datos_finales)

        df = pd.DataFrame(datos_finales)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', 60)

        print("\n\n" + "═"*100)
        print(f"📋 REPORTE FINAL - RESPONSABLE: {ENCARGADA}")
        print("═"*100)
        # Visualización ajustada con las nuevas cabeceras
        print(df[['nombre_producto', 'marca', 'precio']].to_string(index=False))
        print("═"*100)
        print(f"📊 TOTAL PRODUCTOS: {len(df)}")
        print("═"*100)

if __name__ == "__main__":
    ejecutar_mega_extraccion()