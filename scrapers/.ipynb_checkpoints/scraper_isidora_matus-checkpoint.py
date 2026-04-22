# scrapers/scraper_isidora_matus.py
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

def ejecutar_extraccion():
    """Isidora Matus - CUGAT Despensa - Retorna lista de productos"""
    
    # Limpieza inicial
    os.system("pkill -9 chrome")
    os.system("pkill -9 chromedriver")
    os.system("rm -rf /tmp/.com.google.Chrome.*")
    os.system("rm -rf /tmp/.org.chromium.Chromium.*")
    
    datos_finales = []
    driver = None
    
    def limpiar_precio_chileno(precio_texto):
        if not precio_texto: return 0.0
        precio_limpio = re.sub(r'[^\d,]', '', precio_texto)
        precio_limpio = precio_limpio.replace(',', '.')
        try:
            return float(precio_limpio)
        except:
            return 0.0

    def extraer_categoria_especifica(bloque, driver):
        categoria_selectors = [
            ".posted_in a",
            ".product-cats a", 
            ".category a",
            ".product-category a"
        ]
        
        for selector in categoria_selectors:
            try:
                cat_elem = bloque.find_element(By.CSS_SELECTOR, selector)
                categoria = cat_elem.text.strip().lower()
                if categoria and categoria not in ['inicio', 'despensa', 'tienda', 'cugat']:
                    return cat_elem.text.strip()
            except:
                continue
        
        try:
            breadcrumb = driver.find_element(By.CSS_SELECTOR, ".woocommerce-breadcrumb")
            links = breadcrumb.find_elements(By.TAG_NAME, "a")
            if len(links) > 2:
                return links[-2].text.strip()
        except:
            pass
        
        url_actual = driver.current_url.lower()
        categorias_url = {
            'harinas': 'Harinas',
            'levaduras': 'Levaduras', 
            'aceites': 'Aceites',
            'condimentos': 'Condimentos',
            'pastas': 'Pastas'
        }
        for cat_url, cat_nombre in categorias_url.items():
            if cat_url in url_actual:
                return cat_nombre
        
        return "Despensa"

    def detectar_marca(nombre):
        nombre_lower = nombre.lower()
        marcas_despensa = {
            'linderos': 'Linderos',
            'harina': 'Harina Genérica',
            'levadura': 'Levadura',
            'royal': 'Royal',
            'maizena': 'Maizena',
            'costeño': 'Costeño',
            'don': 'Don',
            'lucchetti': 'Lucchetti',
            'knorr': 'Knorr',
            'maggi': 'Maggi',
            'molino': 'Molino',
            'cristal': 'Cristal',
            'puro': 'Puro Aceite',
            'santa clara': 'Santa Clara',
            'colun': 'Colun'
        }
        
        for marca_key, marca_nombre in marcas_despensa.items():
            if marca_key in nombre_lower:
                return marca_nombre
        return "Cugat Propio"

    # Configuración Chrome
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        driver = webdriver.Chrome(options=options)
        print("🚀 ISIDORA MATUS - CUGAT Despensa iniciado")
        
        URL_CUGAT = "https://cugat.cl/categoria-producto/despensa/"
        driver.get(URL_CUGAT)
        time.sleep(5)

        limite_paginas = 10
        pagina = 1

        while pagina <= limite_paginas:
            print(f"\n📄 ISIDORA MATUS - CUGAT Página {pagina}")
            time.sleep(3)

            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".woocommerce-loop-product__link"))
            )

            bloques = driver.find_elements(By.CSS_SELECTOR, ".product, .woocommerce-loop-product")

            for bloque in bloques:
                try:
                    # NOMBRE
                    nombre = "N/A"
                    nombre_selectors = [
                        ".woocommerce-loop-product__title",
                        "h2.woocommerce-loop-product__title",
                        "h2 a", "h3 a", ".product_title"
                    ]
                    
                    for selector in nombre_selectors:
                        try:
                            nombre_elem = bloque.find_element(By.CSS_SELECTOR, selector)
                            nombre = nombre_elem.text.strip()
                            if len(nombre) > 3:
                                break
                        except:
                            continue

                    if len(nombre) < 3:
                        continue

                    # PRECIO
                    precio = 0.0
                    precio_selectors = [
                        ".price .woocommerce-Price-amount.amount",
                        ".price", ".woocommerce-Price-amount", ".amount"
                    ]
                    
                    for selector in precio_selectors:
                        try:
                            precio_elem = bloque.find_element(By.CSS_SELECTOR, selector)
                            precio_texto = precio_elem.text.strip()
                            precio = limpiar_precio_chileno(precio_texto)
                            if precio > 0:
                                break
                        except:
                            continue

                    if precio == 0:
                        continue

                    # CATEGORÍA Y MARCA
                    categoria = extraer_categoria_especifica(bloque, driver)
                    marca = detectar_marca(nombre)

                    # URL
                    url_producto = "N/A"
                    try:
                        link_elem = bloque.find_element(By.CSS_SELECTOR, "a.woocommerce-LoopProduct-link")
                        url_producto = link_elem.get_attribute("href")
                    except:
                        try:
                            link_elem = bloque.find_element(By.TAG_NAME, "a")
                            url_producto = link_elem.get_attribute("href")
                        except:
                            pass

                    # ✅ FORMATO PARA TU FRAMEWORK
                    producto = {
                        "identificador": re.sub(r'[^\w\s-]', '', nombre)[:100],
                        "nombre": nombre,
                        "valor": precio,           # ← Campo requerido
                        "categoria": categoria,    # ← Categorías específicas
                        "marca": marca,            # ← Marcas detectadas
                        "supermercado": "Cugat",
                        "grupo": "Isidora Matus",  # ← TU identificador
                        "url_producto": url_producto,
                        "fecha_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    datos_finales.append(producto)
                    print(f"   ✅ {nombre[:40]}... | ${precio:,.0f} | {categoria} | {marca}")

                except:
                    continue

            # Siguiente página
            try:
                btn_sig = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next:not(.disabled)"))
                )
                driver.execute_script("arguments[0].click();", btn_sig)
                time.sleep(4)
                pagina += 1
            except:
                break

        print(f"🎉 ISIDORA MATUS - CUGAT: {len(datos_finales)} productos")
        return datos_finales

    except Exception as e:
        print(f"❌ ISIDORA MATUS - Error: {e}")
        return datos_finales

    finally:
        if driver:
            driver.quit()

# Prueba standalone
if __name__ == "__main__":
    datos = ejecutar_extraccion()
    print(f"\n✅ Isidora Matus - Total: {len(datos)} productos CUGAT")