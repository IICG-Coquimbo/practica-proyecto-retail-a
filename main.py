# --- Al principio del archivo, donde están los imports ---
from scrapers import scraper_felipe  # Tu scraper
from scrapers import scraper_soto    # El de tu compañero
from scrapers import scraper_renato

# --- Dentro de la lógica donde se ejecutan los scrapers ---
print("Ejecutando scraper de Felipe...")
datos_felipe = scraper_felipe.ejecutar_extraccion()

print("Ejecutando scraper de Renato (Unimarc)...")
datos_renato = scraper_renato.ejecutar_extraccion()

# Luego estos datos se unirán para ir a Spark/MongoDB
datos_totales = datos_felipe + datos_soto + datos_renato