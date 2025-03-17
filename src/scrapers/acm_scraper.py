from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from src.drivers.web_driver import setup_driver, handle_cookie_dialog

def fetch_data_from_page(url, page_number):
    """Extrae datos de artículos de una página específica de ACM Digital Library"""
    driver = setup_driver()
    data = []
    try:
        print(f"Scraping página {page_number + 1}...")
        driver.get(url)
        
        # Manejar el diálogo de cookies
        handle_cookie_dialog(driver)
        
        # Esperar a que aparezca al menos un elemento de título
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'issue-item__title'))
        )
        # Tiempo de espera reducido
        time.sleep(2)

        results = driver.find_elements(By.CLASS_NAME, 'issue-item')
        for result in results:
            try:
                title_element = result.find_element(By.CLASS_NAME, 'issue-item__title')
                title = title_element.text.strip()
                
                author_elements = result.find_elements(By.CSS_SELECTOR, '.loa a span')
                authors = ', '.join([author.text for author in author_elements]) if author_elements else "Unknown"
                
                year_element = result.find_element(By.CSS_SELECTOR, '.bookPubDate.simple-tooltip__block--b')
                year = year_element.text.split()[-1] if year_element else "Unknown"
                
                abstract_element = result.find_element(By.CLASS_NAME, 'issue-item__abstract')
                abstract = abstract_element.text.strip() if abstract_element else "No abstract available"
                
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
                continue
                
        print(f"Encontrados {len(data)} artículos en la página {page_number + 1}")
    except Exception as e:
        print(f"Error en la página {page_number + 1} ({url}): {e}")
    finally:
        driver.quit()
    return data


def fetch_data_from_acm(total_pages):
    """Extrae datos de múltiples páginas de resultados de ACM Digital Library"""
    base_url = 'https://dl.acm.org/action/doSearch?AllField=computational+thinking&pageSize=50&startPage='
    all_data = []

    for page_number in range(total_pages):
        url = base_url + str(page_number)
        page_data = fetch_data_from_page(url, page_number)
        all_data.extend(page_data)

        # Pausa corta entre páginas para evitar sobrecarga del servidor
        if page_number < total_pages - 1:
            time.sleep(1)  # Reducir el tiempo de espera si es necesario

    print(f"Total de artículos extraídos: {len(all_data)}")
    return all_data