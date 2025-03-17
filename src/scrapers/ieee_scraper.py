import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def setup_driver():
    """Configura y devuelve un driver de Chrome para Selenium"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver


def fetch_data_from_ieee(total_pages):
    """Extrae datos de múltiples páginas de resultados de IEEE Xplore"""
    base_url = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=computational%20thinking&pageNumber='
    all_data = []

    driver = setup_driver()
    try:
        for page_number in range(1, total_pages + 1):
            url = base_url + str(page_number)
            driver.get(url)

            # Esperar a que se carguen los resultados
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'List-results-items'))
            )

            # Extraer datos de la página
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = soup.find_all('div', class_='List-results-items')

            for result in results:
                try:
                    title_element = result.find('h2')
                    title = title_element.text.strip() if title_element else "No title available"

                    author_elements = result.find_all('a', class_='author')
                    authors = ', '.join([a.text.strip() for a in author_elements]) if author_elements else "Unknown"

                    description_element = result.find('div', class_='description')
                    year = description_element.text.split()[-1] if description_element else "Unknown"

                    abstract_element = result.find('div', class_='abstract')
                    abstract = abstract_element.text.strip() if abstract_element else "No abstract available"

                    all_data.append({
                        'title': title,
                        'author': authors,
                        'year': year,
                        'abstract': abstract
                    })
                except Exception as e:
                    print(f"Error procesando un artículo: {e}")
                    continue

            print(f"Página {page_number} procesada. Artículos encontrados: {len(results)}")

            # Pausa corta entre páginas para evitar sobrecarga del servidor
            if page_number < total_pages:
                time.sleep(1)  # Reducir el tiempo de espera si es necesario

    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")
    finally:
        driver.quit()

    print(f"Total de artículos extraídos: {len(all_data)}")
    return all_data