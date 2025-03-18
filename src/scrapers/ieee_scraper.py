import os
import time
import re
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


def extract_text_from_element(element):
    """Extrae texto plano de un elemento que puede contener etiquetas HTML"""
    if not element:
        return ""
    # Limpia el texto eliminando etiquetas HTML y espacios adicionales
    return re.sub(r'\s+', ' ', element.get_text(strip=True))


def fetch_data_from_ieee(total_pages):
    """Extrae datos de múltiples páginas de resultados de IEEE Xplore"""
    base_url = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=computational%20thinking&pageNumber='
    all_data = []

    driver = setup_driver()
    try:
        for page_number in range(1, total_pages + 1):
            url = base_url + str(page_number)
            print(f"\nNavegando a la página {page_number}: {url}")
            driver.get(url)

            # Esperar a que se carguen los resultados (usando el nuevo selector)
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'xpl-results-item'))
                )
            except TimeoutException:
                print(f"Tiempo de espera agotado en la página {page_number}. Intentando con otro selector...")
                try:
                    # Intentar con un selector alternativo
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'result-item'))
                    )
                except TimeoutException:
                    print(f"No se pudieron cargar los resultados en la página {page_number}. Pasando a la siguiente.")
                    continue

            # Dar tiempo adicional para asegurar que todo se haya cargado
            time.sleep(3)

            # Extraer datos de la página
            print(f"Extrayendo datos de la página {page_number}...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Intentar con los nuevos selectores
            results = soup.find_all('xpl-results-item') or soup.find_all('div', class_='result-item')
            
            if not results:
                print(f"No se encontraron resultados en la página {page_number} con los selectores principales.")
                # Intentar con un selector más general
                results = soup.find_all('div', attrs={'_ngcontent-ng-c3757591678': ''})
            
            print(f"Se encontraron {len(results)} elementos en la página {page_number}")

            for result in results:
                try:
                    # Extraer título (nuevo selector)
                    title_element = result.find('h3', class_='result-item-title') or result.find('h2')
                    title = ""
                    
                    if title_element:
                        # Buscar el enlace dentro del título, que contiene el texto
                        title_link = title_element.find('a')
                        if title_link:
                            title = extract_text_from_element(title_link)
                        else:
                            title = extract_text_from_element(title_element)
                    
                    if not title:
                        title = "No title available"
                    
                    # Extraer autores (nuevo selector)
                    author_container = result.find('p', class_='author') or result.find('div', class_='author')
                    authors = "Unknown"
                    
                    if author_container:
                        author_links = author_container.find_all('a')
                        if author_links:
                            authors = ', '.join([extract_text_from_element(a) for a in author_links])
                    
                    # Extraer año y tipo de publicación (nuevo selector)
                    year = "Unknown"
                    pub_type = "Unknown"
                    
                    publisher_info = result.find('div', class_='publisher-info-container')
                    if publisher_info:
                        # Buscar el año
                        year_span = publisher_info.find('span', string=lambda text: text and 'Year:' in text)
                        if year_span:
                            year = year_span.text.replace('Year:', '').strip()
                        
                        # Buscar el tipo de publicación
                        pub_type_span = publisher_info.find_all('span')
                        for span in pub_type_span:
                            text = span.text.strip()
                            if text in ['Conference Paper', 'Journal Article', 'Early Access Article']:
                                pub_type = text
                                break
                    
                    # Si no se encontró el año o el tipo, intentar con otros selectores
                    if year == "Unknown":
                        description = result.find('div', class_='description')
                        if description:
                            # Buscar patrones de año (4 dígitos)
                            year_match = re.search(r'\b(19|20)\d{2}\b', description.text)
                            if year_match:
                                year = year_match.group(0)
                    
                    # Extraer abstract
                    abstract = "No abstract available"
                    abstract_element = result.find('div', class_='js-displayer-content') or result.find('div', class_='abstract')
                    if abstract_element:
                        abstract = extract_text_from_element(abstract_element)
                    
                    # Agregar datos extraídos
                    article_data = {
                        'title': title,
                        'author': authors,
                        'year': year,
                        'abstract': abstract,
                        'publication_type': pub_type
                    }
                    
                    all_data.append(article_data)
                    print(f"Extraído: {title} ({year})")
                    
                except Exception as e:
                    print(f"Error procesando un artículo: {e}")
                    continue

            print(f"Página {page_number} procesada. Artículos encontrados: {len(results)}")

            # Pausa corta entre páginas para evitar sobrecarga del servidor
            if page_number < total_pages:
                print(f"Esperando antes de cargar la página {page_number + 1}...")
                time.sleep(2)

    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")
    finally:
        driver.quit()

    print(f"Total de artículos extraídos: {len(all_data)}")
    return all_data


# Para pruebas directas del script
if __name__ == "__main__":
    total_pages = 1
    print(f"Iniciando extracción de {total_pages} páginas de IEEE Xplore...")
    articles = fetch_data_from_ieee(total_pages)
    
    # Mostrar una muestra de los resultados
    for i, article in enumerate(articles[:3], 1):
        print(f"\nArtículo {i}:")
        print(f"Título: {article['title']}")
        print(f"Autores: {article['author']}")
        print(f"Año: {article['year']}")
        print(f"Tipo: {article['publication_type']}")
        print(f"Abstract: {article['abstract'][:100]}...")