import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para permitir importaciones absolutas
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.scrapers.acm_scraper import fetch_data_from_acm
from src.scrapers.sciencedirect_scraper import fetch_data_from_sciencedirect
from src.formatters.bibtex_formatter import save_to_bibtex
from src.processors.data_processor import remove_duplicates_and_save

def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    # Ensure directories exist
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)

    # Fetch data from ACM
    acm_pages =  1 # Set the number of pages to scrape
    print(f"\n=== Iniciando extracción de {acm_pages} páginas de ACM Digital Library ===")
    acm_data = fetch_data_from_acm(acm_pages)
    raw_acm_file = os.path.join(raw_data_path, 'acm_data.bib')
    save_to_bibtex(acm_data, raw_acm_file)
    print(f"Datos sin procesar de ACM guardados en: {raw_acm_file}")

    # Fetch data from ScienceDirect
    sciencedirect_pages = 3  # Set the number of pages to scrape
    print(f"\n=== Iniciando extracción de {sciencedirect_pages} páginas de ScienceDirect ===")
    sciencedirect_file = os.path.join(raw_data_path, 'sciencedirect_data.bib')
    fetch_data_from_sciencedirect(sciencedirect_pages, sciencedirect_file)

    # Process and combine data from both sources
    # Aquí se podría implementar un procesador para combinar ambos archivos BibTeX
    # y eliminar duplicados entre las distintas fuentes
    
    # Por ahora, solo procesamos los datos de ACM
    unique_file_path = os.path.join(processed_data_path, 'unique_entries.bib')
    duplicates_file_path = os.path.join(processed_data_path, 'duplicates.json')
    remove_duplicates_and_save(acm_data, unique_file_path, duplicates_file_path)
    
    print("\nProceso completado con éxito.")

if __name__ == "__main__":
    main()