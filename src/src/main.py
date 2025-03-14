import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pybtex.database
from pybtex.database.output import bibtex as bibtex_output
import json
import re
import hashlib

def setup_driver():
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # Añadir opciones para mejorar el rendimiento
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_data_from_page(url, page_number):
    driver = setup_driver()
    data = []
    try:
        print(f"Scraping página {page_number + 1}...")
        driver.get(url)
        # Esperar a que aparezca al menos un elemento de título
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'issue-item__title'))
        )
        # Reducir el tiempo de espera a 2 segundos
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
    base_url = 'https://dl.acm.org/action/doSearch?AllField=computational+thinking&pageSize=50&startPage='
    all_data = []

    for page_number in range(total_pages):
        url = base_url + str(page_number)
        page_data = fetch_data_from_page(url, page_number)
        all_data.extend(page_data)
        # Pausa corta entre páginas para evitar sobrecarga del servidor
        if page_number < total_pages - 1:
            time.sleep(1)

    print(f"Total de artículos extraídos: {len(all_data)}")
    return all_data

def generate_safe_bibtex_id(title, author):
    """Genera un ID BibTeX seguro basado en el título y autor"""
    # Crear un hash corto pero único basado en título y autor
    hash_input = (title + author).encode('utf-8')
    hash_id = hashlib.md5(hash_input).hexdigest()[:8]
    
    # Crear un prefijo con el primer autor y año si está disponible
    prefix = ""
    if author and "," in author:
        first_author = author.split(",")[0].strip()
        # Tomar solo el apellido si hay múltiples nombres
        if " " in first_author:
            prefix = first_author.split()[-1]
        else:
            prefix = first_author
    
    # Eliminar caracteres no válidos y convertir a minúsculas
    if prefix:
        prefix = re.sub(r'[^\w]', '', prefix).lower()
        return f"{prefix}_{hash_id}"
    else:
        return f"entry_{hash_id}"

def save_to_bibtex(data, file_path):
    bib_data = pybtex.database.BibliographyData()
    for entry in data:
        fields = {
            'title': entry['title'],
            'author': entry['author'],
            'year': entry['year'],
            'abstract': entry['abstract']
        }
        bib_entry = pybtex.database.Entry('article', fields=fields)
        entry_id = generate_safe_bibtex_id(entry['title'], entry['author'])
        bib_data.entries[entry_id] = bib_entry
    
    writer = bibtex_output.Writer()
    with open(file_path, 'w', encoding='utf-8') as bibfile:
        writer.write_stream(bib_data, bibfile)

def remove_duplicates_and_save(data, unique_file_path, duplicates_file_path):
    unique_entries = []
    duplicates = []
    seen_titles = {}  # Diccionario para rastrear títulos y sus índices

    for entry in data:
        title = entry['title'].lower().strip()
        if title not in seen_titles:
            seen_titles[title] = len(unique_entries)
            unique_entries.append(entry)
        else:
            # Verificar si la entrada actual tiene más información que la existente
            existing_entry = unique_entries[seen_titles[title]]
            if (len(entry['abstract']) > len(existing_entry['abstract']) and 
                existing_entry['abstract'] == "No abstract available"):
                # Reemplazar la entrada existente con esta más completa
                unique_entries[seen_titles[title]] = entry
                duplicates.append(existing_entry)
            else:
                duplicates.append(entry)

    # Save unique entries to BibTeX
    save_to_bibtex(unique_entries, unique_file_path)
    print(f"Archivo de registros únicos guardado en: {unique_file_path}")
    print(f"Entradas únicas: {len(unique_entries)}")

    # Save duplicates to JSON
    with open(duplicates_file_path, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, indent=4, ensure_ascii=False)
    print(f"Archivo de registros duplicados guardado en: {duplicates_file_path}")
    print(f"Entradas duplicadas: {len(duplicates)}")

def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    # Ensure directories exist
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)

    # Fetch data from ACM
    total_pages = 5  # Set the number of pages to scrape
    print(f"Iniciando extracción de {total_pages} páginas de ACM Digital Library...")
    acm_data = fetch_data_from_acm(total_pages)

    # Save raw data to BibTex files
    raw_acm_file = os.path.join(raw_data_path, 'acm_data.bib')
    save_to_bibtex(acm_data, raw_acm_file)
    print(f"Datos sin procesar guardados en: {raw_acm_file}")

    # Remove duplicates and save unique and duplicate entries
    unique_file_path = os.path.join(processed_data_path, 'unique_entries.bib')
    duplicates_file_path = os.path.join(processed_data_path, 'duplicates.json')
    remove_duplicates_and_save(acm_data, unique_file_path, duplicates_file_path)
    
    print("Proceso completado con éxito.")

if __name__ == "__main__":
    main()