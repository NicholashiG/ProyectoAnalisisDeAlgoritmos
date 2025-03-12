import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pybtex.database
from pybtex.database.output import bibtex as bibtex_output


def setup_driver(profile_path=None):
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# Se obtiene la data de ACM
def fetch_data_from_acm(driver):
    driver.get('https://dl.acm.org/action/doSearch?AllField=computational+thinking')
    try:
        # Wait for the search results to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'issue-item__title'))
        )
        time.sleep(5)  # Wait for the page to load completely

        # Extract data from the search results
        results = driver.find_elements(By.CLASS_NAME, 'issue-item')
        data = []
        for result in results:
            title_element = result.find_element(By.CLASS_NAME, 'issue-item__title')
            title = title_element.text

            # Try to find the authors
            try:
                author_elements = result.find_elements(By.CSS_SELECTOR, '.loa a span')
                authors = ', '.join([author.text for author in author_elements])
            except:
                authors = "Unknown"

            # Try to find the year
            try:
                year_element = result.find_element(By.CSS_SELECTOR, '.bookPubDate.simple-tooltip__block--b')
                year = year_element.text.split()[-1]
            except:
                year = "Unknown"

            # Try to find the abstract
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


def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    # Load and clean data
    # cleaned_data = load_and_clean_data(raw_data_path)

    # Generate statistics
    # statistics = generate_statistics(cleaned_data)

    # Measure textual similarity
    # similarity_results = measure_textual_similarity(cleaned_data)

    # Visualize results
    # visualize_results(statistics, similarity_results)

    driver = setup_driver()

    # Fetch data from ACM
    acm_data = fetch_data_from_acm(driver)

    # Save raw data to BibTex files
    save_to_bibtex(acm_data, 'acm_data.bib')

    # Repeat similar steps for other databases (ScienceDirect, Scopus)

    driver.quit()


if __name__ == "__main__":
    main()