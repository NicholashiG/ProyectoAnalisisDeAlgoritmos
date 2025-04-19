import os
import json
import sys
import glob

# Agregar el directorio raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora importar los módulos
from src.scrapers.acm_scraper import fetch_data_from_acm
from src.scrapers.ieee_scraper import fetch_data_from_ieee
from src.scrapers.sciencedirect_scraper import fetch_data_from_sciencedirect
from src.processors.data_processor import remove_duplicates_and_save
from src.formatters.bibtex_formatter import save_to_bibtex
from src.reader_resourses.algorithmsExecution import AlgorithmsExecution
from src.processors.statistics_generator import generate_all_statistics


def ejecutar_scrapers(num_pages, raw_data_path):
    # Fetch data from ScienceDirect
    print(f"\n=== Iniciando extracción de {num_pages} páginas de ScienceDirect ===")
    sciencedirect_data = fetch_data_from_sciencedirect(num_pages)
    
    # Save raw ScienceDirect data
    sciencedirect_raw_file = os.path.join(raw_data_path, 'sciencedirect_data.bib')
    save_to_bibtex(sciencedirect_data, sciencedirect_raw_file)
    print(f"Datos sin procesar de ScienceDirect guardados en: {sciencedirect_raw_file}")

    # Fetch data from ACM
    print(f"\n=== Iniciando extracción de {num_pages} páginas de ACM Digital Library ===")
    acm_data = fetch_data_from_acm(num_pages)
    
    # Save raw ACM data
    acm_raw_file = os.path.join(raw_data_path, 'acm_data.bib')
    save_to_bibtex(acm_data, acm_raw_file)
    print(f"Datos sin procesar de ACM guardados en: {acm_raw_file}")

    # Fetch data from IEEE
    print(f"\n=== Iniciando extracción de {num_pages} páginas de IEEE Xplore ===")
    ieee_data = fetch_data_from_ieee(num_pages)
    
    # Save raw IEEE data
    ieee_raw_file = os.path.join(raw_data_path, 'ieee_data.bib')
    save_to_bibtex(ieee_data, ieee_raw_file)
    print(f"Datos sin procesar de IEEE guardados en: {ieee_raw_file}")
    
    # Combine data from all sources (mismo orden que la extracción)
    return sciencedirect_data + acm_data + ieee_data


def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')
    unique_file_path = os.path.join(processed_data_path, 'unique_entries.bib')
    duplicates_file_path = os.path.join(processed_data_path, 'duplicates.json')
    statistics_folder = os.path.join(processed_data_path, 'statistics')

    # Ensure directories exist
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)
    os.makedirs(statistics_folder, exist_ok=True)

    # Ejecutar todos los scrapers con 30 páginas cada uno
    """
    num_pages = 30
    combined_data = ejecutar_scrapers(num_pages, raw_data_path)
    """
    
    # Cargar datos de todos los archivos BibTeX en data/raw
    #combined_data = cargar_datos_bibtex_desde_carpeta(raw_data_path)
    
    # Remove duplicates and save unique entries
    """
    unique_entries, duplicates = remove_duplicates_and_save(combined_data, unique_file_path, duplicates_file_path)
    """
    
    # Cargar títulos directamente del archivo de entradas únicas para el análisis de ordenamiento
    # Procesamiento más eficiente - extrae solo los títulos sin cargar todo el archivo en memoria
    print("\n=== Cargando títulos para algoritmos de ordenamiento ===")
    titles = []
    with open(unique_file_path, 'r', encoding='utf-8') as bibfile:
        for line in bibfile:
            line = line.strip()
            if line.startswith('title = {'):
                # Extraer el título entre llaves
                title = line.replace('title = {', '').rstrip(',}')
                # Manejar títulos que abarcan varias líneas
                while '},' not in title and '}' not in title:
                    next_line = next(bibfile, '').strip()
                    title += ' ' + next_line
                title = title.rstrip(',}')
                titles.append(title)
    
    print(f"Cargados {len(titles)} títulos para análisis de algoritmos de ordenamiento.")
    
    # Execute sorting algorithms on titles
    print("\n=== Ejecutando algoritmos de ordenamiento ===")
    algorithms_execution = AlgorithmsExecution()
    results = algorithms_execution.execute_algorithms(titles, "Títulos")
    
    # Save results to a table
    sorting_results_path = os.path.join(processed_data_path, 'sorting_results.json')
    with open(sorting_results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Resultados de ordenamiento guardados en: {sorting_results_path}")

    # Generate publication statistics using direct file processing
    print("\n=== Generando estadísticas de publicaciones ===")
    stats_report = generate_all_statistics(
        bibtex_data=unique_file_path,
        output_folder=statistics_folder,
        data_is_file=True  # Usar procesamiento directo de archivo
    )
    print(f"Estadísticas generadas en: {stats_report}")

    print("\nProceso completado con éxito.")


if __name__ == "__main__":
    main()