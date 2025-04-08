import json
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para permitir importaciones absolutas
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Ahora importamos correctamente los módulos
from src.scrapers.acm_scraper import fetch_data_from_acm
from src.scrapers.ieee_scraper import fetch_data_from_ieee
from src.scrapers.sciencedirect_scraper import fetch_data_from_sciencedirect
from src.processors.data_processor import remove_duplicates_and_save
from src.formatters.bibtex_formatter import save_to_bibtex
from src.reader_resourses.algorithmsExecution import AlgorithmsExecution


def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    # Ensure directories exist
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)

    # Fetch data from IEEE (ahora tercero)
    ieee_pages = 2  # Número de páginas a extraer de IEEE
    print(f"\n=== Iniciando extracción de {ieee_pages} páginas de IEEE Xplore ===")
    ieee_data = fetch_data_from_ieee(ieee_pages)

    # Save raw IEEE data
    ieee_raw_file = os.path.join(raw_data_path, 'ieee_data.bib')
    save_to_bibtex(ieee_data, ieee_raw_file)
    print(f"Datos sin procesar de IEEE guardados en: {ieee_raw_file}")

    # Combine data from all sources (mismo orden que la extracción)
    combined_data =  ieee_data

    # Remove duplicates and save unique entries
    unique_file_path = os.path.join(processed_data_path, 'unique_entries.bib')
    duplicates_file_path = os.path.join(processed_data_path, 'duplicates.json')
    unique_entries, duplicates = remove_duplicates_and_save(combined_data, unique_file_path, duplicates_file_path)

    # Extract titles for sorting analysis
    titles = [entry['title'] for entry in unique_entries]

    # Execute sorting algorithms on titles
    algorithms_execution = AlgorithmsExecution()
    results = algorithms_execution.execute_algorithms(titles, "Títulos")

    # Save results to a table (optional)
    sorting_results_path = os.path.join(processed_data_path, 'sorting_results.json')
    with open(sorting_results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\nProceso completado con éxito.")


if __name__ == "__main__":
    main()