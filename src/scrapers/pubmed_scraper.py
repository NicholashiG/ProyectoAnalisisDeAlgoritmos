from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from src.drivers.web_driver import setup_driver, handle_cookie_dialog


def fetch_data_from_pubmed_page(url, page_number):
    """Extrae datos de artículos de una página específica de PubMed"""
    driver = setup_driver()
    data = []
    try:
        print(f"Scraping página {page_number + 1} de PubMed...")
        driver.get(url)

        # Esperar a que aparezca al menos un elemento de título
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'docsum-content'))
        )
        # Tiempo de espera reducido
        time.sleep(2)

        results = driver.find_elements(By.CLASS_NAME, 'docsum-content')
        for result in results:
            try:
                # Extraer el título
                title_element = result.find_element(By.CSS_SELECTOR, 'a.docsum-title')
                title = title_element.text.strip()

                # Extraer los autores
                author_elements = result.find_elements(By.CSS_SELECTOR, 'span.docsum-authors')
                authors = ', '.join([author.text for author in author_elements]) if author_elements else "Unknown"

                # Extraer el año
                year_element = result.find_element(By.CSS_SELECTOR, 'span.docsum-journal-citation')
                year = year_element.text.split()[-1] if year_element else "Unknown"  # El año suele ser la última palabra

                # Extraer el resumen (PubMed no muestra resúmenes en la página de resultados)
                abstract = "No abstract available"

                # Solo añadir si el título no está vacío
                if title:
                    data.append({
                        'title': title,
                        'author': authors,
                        'year': year,
                        'abstract': abstract
                    })
            except Exception as e:
                # Ignorar elementos que no se pueden procesar correctamente
                print(f"Error al procesar un artículo: {e}")
                continue

        print(f"Encontrados {len(data)} artículos en la página {page_number + 1} de PubMed")
    except Exception as e:
        print(f"Error en la página {page_number + 1} de PubMed ({url}): {e}")
    finally:
        driver.quit()
    return data


def fetch_data_from_pubmed(total_pages):
    """Extrae datos de múltiples páginas de resultados de PubMed"""
    base_url = 'https://pubmed.ncbi.nlm.nih.gov/?term=computational+thinking&page='
    all_data = []

    for page_number in range(total_pages):
        url = base_url + str(page_number + 1)  # PubMed empieza en página 1
        page_data = fetch_data_from_pubmed_page(url, page_number)
        all_data.extend(page_data)

        # Pausa corta entre páginas para evitar sobrecarga del servidor
        if page_number < total_pages - 1:
            time.sleep(1)  # Reducir el tiempo de espera si es necesario

    print(f"Total de artículos extraídos de PubMed: {len(all_data)}")
    return all_data