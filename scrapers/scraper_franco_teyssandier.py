import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def ejecutar_extraccion():
    # Limpieza inicial de procesos
    os.system("pkill -9 chrome")
    print("Limpieza OK")

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--headless") 

    driver = webdriver.Chrome(options=options)
    datos_finales = []
    categoria_obj = {"nombre": "Lacteos y Congelados"}

    try:
        # Bucle de paginación (1 a 19)
        for num_pagina in range(1, 20):
            url_base = f"https://www.santaisabel.cl/despensa?page={num_pagina}"
            
            print(f"\n--- PROCESANDO: {url_base} ---")
            driver.get(url_base)
            
            time.sleep(10) 
            driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(3)

            # Localización de contenedores
            bloques = driver.find_elements(By.CSS_SELECTOR, 
                "div[class*='product'], div[class*='Product'], div[class*='item'], div[class*='tile'], article"
            )
            
            nombres_validos = set()
            exitosos_pagina = 0
            
            for bloque in bloques:
                try:
                    # Extracción por clase específica proporcionada
                    try:
                        nombre_elem = bloque.find_element(By.CSS_SELECTOR, ".product-card-name")
                        nombre_raw = nombre_elem.text.strip()
                    except:
                        continue
                    
                    if not nombre_raw: continue
                    
                    # --- AJUSTE CORRECTOR DE PRECIO (HTML SANTA ISABEL) ---
                    precio_numerico = 0.0
                    try:
                        # Buscamos el contenedor principal de precios con flex e items-baseline
                        contenedor_precio = bloque.find_element(By.CSS_SELECTOR, "div[class*='items-baseline'][class*='text-lg']")
                        p_texto = contenedor_precio.text.strip()
                        
                        # Si viene el precio de oferta y el normal juntos, cortamos en el segundo '$'
                        if "$" in p_texto:
                            partes = p_texto.split("$")
                            p_texto_oferta = partes[1]  # Aísla el primer valor numérico (Oferta)
                        else:
                            p_texto_oferta = p_texto
                            
                        p_limpio = ''.join(c for c in p_texto_oferta if c.isdigit())
                        if p_limpio:
                            precio_numerico = float(p_limpio)
                    except:
                        # Fallback tradicional de respaldo si no encuentra las clases dinámicas anteriores
                        precio_elems = bloque.find_elements(By.XPATH, ".//*[contains(text(), '$')]")
                        for p_elem in precio_elems:
                            p_texto = p_elem.text.strip()
                            if any(unit in p_texto.lower() for unit in ['x un', 'x kg', 'x lt']): continue
                            p_limpio = ''.join(c for c in p_texto if c.isdigit())
                            if len(p_limpio) >= 3:
                                # Si por error el fallback junta ambos precios, dividimos el largo por seguridad
                                if len(p_limpio) > 5:
                                    p_limpio = p_limpio[:int(len(p_limpio)/2)]
                                precio_numerico = float(p_limpio)
                                break
                    
                    # --- AJUSTE EXTRACCIÓN DE MARCA DINÁMICA ---
                    marca_producto = "No especificada"
                    try:
                        # Buscamos el elemento de párrafo gris (<p>) correspondiente a la marca
                        marca_elem = bloque.find_element(By.CSS_SELECTOR, "p[class*='text-gray-500'], p[class*='mb-1']")
                        marca_texto = marca_elem.text.strip()
                        if marca_texto and len(marca_texto) < 30:
                            marca_producto = marca_texto
                    except:
                        pass
                    
                    fecha_ahora = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    url_imagen = "No disponible"
                    try:
                        img_elem = bloque.find_element(By.TAG_NAME, "img")
                        url_imagen = img_elem.get_attribute("src")
                    except:
                        pass

                    # Validación y guardado con el formato de fusión solicitado
                    if precio_numerico > 0 and nombre_raw not in nombres_validos:
                        nombres_validos.add(nombre_raw)
                        
                        # FUSION DE FORMATOS: Datos originales + Identificadores solicitados
                        datos_finales.append({
                            "nombre_producto": nombre_raw,
                            "precio": round(precio_numerico),
                            "fecha_captura": fecha_ahora,
                            "supermercado": "Santa Isabel",
                            "categoria": categoria_obj["nombre"],
                            "marca": marca_producto,  # <-- Ahora dinámico
                            "imagen": url_imagen,
                            "responsable": "Franco TP"
                        })
                        exitosos_pagina += 1
                            
                except:
                    continue
            
            print(f"Página {num_pagina} finalizada. Items capturados: {exitosos_pagina}")

        print(f"\nEXTRACCION TOTAL FINALIZADA: {len(datos_finales)} productos.")

    except Exception as e:
        print(f"Error durante el proceso: {e}")

    finally:
        driver.quit()
    
    return datos_finales

# Para ejecutar la función:
# resultados = ejecutar_extraccion()