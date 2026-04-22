# --- Al principio del archivo, donde están los imports ---
from scrapers import scraper_felipe  # Tu scraper
from scrapers import scraper_soto    # El de tu compañero

# --- Dentro de la lógica donde se ejecutan los scrapers ---
print("Ejecutando scraper de Felipe...")
datos_felipe = scraper_felipe.ejecutar_extraccion()

print("Ejecutando scraper de Soto...")
datos_soto = scraper_soto.ejecutar_extraccion()

# Luego estos datos se unirán para ir a Spark/MongoDB
datos_totales = datos_felipe + datos_soto