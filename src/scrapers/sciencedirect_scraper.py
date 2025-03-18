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

def wait_for_login(driver):
    """Espera a que el usuario inicie sesión manualmente"""
    print("\n=== INSTRUCCIONES PARA EL LOGIN ===")
    print("1. Se abrirá el navegador en la página de ScienceDirect")
    print("2. Por favor, inicia sesión manualmente")
    print("3. Una vez logueado, el script continuará automáticamente")
    print("===================================\n")
    
    driver.get("https://login.crai.referencistas.com/login?url=https://www.sciencedirect.com")
    
    # Esperar hasta 5 minutos para el login manual
    max_wait_time = 300
    start_time = time.time()
    
    print("Esperando login manual...")
    
    while time.time() - start_time < max_wait_time:
        if "sciencedirect-com.crai" in driver.current_url:
            print("\n¡Login detectado!")
            time.sleep(2)
            return True
        time.sleep(1)
    
    print("Tiempo de espera agotado.")
    return False

def extract_data_from_page(driver, page_number):
    """Extrae datos de artículos de una página específica de ScienceDirect"""
    offset = (page_number - 1) * 100
    url = f"https://www-sciencedirect-com.crai.referencistas.com/search?qs=Computational%20Thinking&show=100&offset={offset}"
    
    print(f"Navegando a la página {page_number}...")
    driver.get(url)
    
    try:
        # Esperar a que se carguen los resultados
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ResultItem"))
        )
        
        # Extraer datos usando BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('li', class_='ResultItem')
        
        page_data = []
        for result in results:
            try:
                # Extraer título
                title_element = result.find('a', class_='result-list-title-link')
                title = title_element.text.strip() if title_element else "No title available"
                
                # Extraer autores
                author_elements = result.find_all('a', class_='author-name')
                authors = ', '.join([author.text.strip() for author in author_elements]) if author_elements else "Unknown"
                
                # Extraer año
                pub_year_element = result.find('span', class_='publication-year')
                year = pub_year_element.text.strip() if pub_year_element else "Unknown"
                
                # Extraer abstract
                abstract_element = result.find('div', class_='result-item-content')
                abstract = abstract_element.text.strip() if abstract_element else "No abstract available"
                
                page_data.append({
                    'title': title,
                    'author': authors,
                    'year': year,
                    'abstract': abstract
                })
            except Exception as e:
                print(f"Error procesando un artículo: {e}")
                continue
        
        print(f"Página {page_number} procesada. Artículos encontrados: {len(page_data)}")
        return page_data
        
    except Exception as e:
        print(f"Error al procesar la página {page_number}: {e}")
        return []

def fetch_data_from_sciencedirect(total_pages):
    """Extrae datos de múltiples páginas de resultados de ScienceDirect"""
    all_data = []
    
    driver = setup_driver()
    try:
        # Esperar a que el usuario complete el login manualmente
        if not wait_for_login(driver):
            print("No se detectó login. Abortando.")
            return all_data
        
        # Extraer datos de cada página
        for page_number in range(1, total_pages + 1):
            page_data = extract_data_from_page(driver, page_number)
            all_data.extend(page_data)
            
            # Pausa corta entre páginas para evitar sobrecarga del servidor
            if page_number < total_pages:
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
    print(f"Iniciando extracción de {total_pages} páginas de ScienceDirect...")
    articles = fetch_data_from_sciencedirect(total_pages)
    print(f"Extracción completada. {len(articles)} artículos encontrados.")