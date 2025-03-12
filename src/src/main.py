import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service  # Importa Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pybtex.database
from pybtex.database.output import bibtex as bibtex_output
import json


def setup_driver(profile_path=None):
    options = webdriver.ChromeOptions()
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")

    # Especifica la ruta del chromedriver descargado manualmente
    driver_path = r"C:\workspace\msedgedriver.exe"  # Ruta completa al archivo

    # Verifica si el archivo chromedriver.exe existe
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"No se encontró el archivo 'chromedriver.exe' en la ruta: {driver_path}")

    # Inicializa el driver de Chrome usando Service
    try:
        service = Service(executable_path=driver_path)  # Usa Service
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error al inicializar el driver de Chrome: {e}")
        raise


def fetch_data_from_acm(driver):
    driver.get('https://dl.acm.org/action/doSearch?AllField=computational+thinking')
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'issue-item__title'))
        )
        time.sleep(5)

        results = driver.find_elements(By.CLASS_NAME, 'issue-item')
        data = []
        for result in results:
            title_element = result.find_element(By.CLASS_NAME, 'issue-item__title')
            title = title_element.text

            try:
                author_elements = result.find_elements(By.CSS_SELECTOR, '.loa a span')
                authors = ', '.join([author.text for author in author_elements])
            except:
                authors = "Unknown"

            try:
                year_element = result.find_element(By.CSS_SELECTOR, '.bookPubDate.simple-tooltip__block--b')
                year = year_element.text.split()[-1]
            except:
                year = "Unknown"

            try:
                abstract_element = result.find_element(By.CLASS_NAME, 'issue-item__abstract')
                abstract = abstract_element.text
            except:
                abstract = "No abstract available"

            data.append({
                'title': title,
                'author': authors,
                'year': year,
                'abstract': abstract
            })
        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


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
        entry_id = entry['title'].replace(' ', '_')
        bib_data.entries[entry_id] = bib_entry
    writer = bibtex_output.Writer()
    with open(file_path, 'w') as bibfile:
        writer.write_stream(bib_data, bibfile)


def remove_duplicates_and_save(data, unique_file_path, duplicates_file_path):
    unique_entries = []
    duplicates = []
    seen_titles = set()

    for entry in data:
        title = entry['title']
        if title not in seen_titles:
            seen_titles.add(title)
            unique_entries.append(entry)
        else:
            duplicates.append(entry)

    save_to_bibtex(unique_entries, unique_file_path)
    print(f"Archivo de registros únicos guardado en: {unique_file_path}")

    with open(duplicates_file_path, 'w') as f:
        json.dump(duplicates, f, indent=4)
    print(f"Archivo de registros duplicados guardado en: {duplicates_file_path}")


def main():
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)

    try:
        driver = setup_driver()

        acm_data = fetch_data_from_acm(driver)

        raw_acm_file = os.path.join(raw_data_path, 'acm_data.bib')
        save_to_bibtex(acm_data, raw_acm_file)

        unique_file_path = os.path.join(processed_data_path, 'unique_entries.bib')
        duplicates_file_path = os.path.join(processed_data_path, 'duplicates.json')
        remove_duplicates_and_save(acm_data, unique_file_path, duplicates_file_path)

    except Exception as e:
        print(f"Error en el proceso principal: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()


if __name__ == "__main__":
    main()