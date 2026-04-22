import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def ejecutar_extraccion():
    datos_finales = []
    
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    
    driver = webdriver.Chrome(options=options)
    base_url = "https://www.santaisabel.cl/lacteos-huevos-y-congelados"

    try:
        for pagina in range(1, 26):
            url = f"{base_url}?page={pagina}" if pagina > 1 else base_url
            driver.get(url)
            time.sleep(6)
            
            bloques = driver.find_elements(By.CSS_SELECTOR, "div[class*='product'], div[class*='Product'], article")
            
            for bloque in bloques:
                try:
                    # Extracción de nombre
                    nombre = "Sin nombre"
                    for selector in ["h3", "h2", ".product-name"]:
                        try:
                            nombre = bloque.find_element(By.CSS_SELECTOR, selector).text.strip()
                            if len(nombre) > 3: break
                        except: continue
                    
                    # Extracción de precio
                    precio = 0
                    p_elems = bloque.find_elements(By.XPATH, ".//*[contains(text(), '$')]")
                    for p_elem in p_elems:
                        p_texto = p_elem.text.strip()
                        if any(u in p_texto.lower() for u in ['x un', 'x kg']): continue
                        p_limpio = re.sub(r'[^\d]', '', p_texto)
                        if len(p_limpio) >= 3:
                            precio = int(p_limpio)
                            break
                    
                    if nombre != "Sin nombre" and precio > 0:
                        datos_finales.append({
                            "identificador": nombre,
                            "valor": precio,
                            "grupo": "Franco_Teyssandier"
                        })
                except:
                    continue
                    
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        driver.quit()

    return datos_finales