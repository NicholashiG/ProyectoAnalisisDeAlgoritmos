import json
import os
import sys
import glob
from pathlib import Path
import bibtexparser

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


def ejecutar_scrapers(num_pages, raw_data_path):
    """
    Ejecuta todos los scrapers y retorna los datos combinados.
    
    Args:
        num_pages (int): Número de páginas a extraer de cada fuente
        raw_data_path (str): Ruta donde guardar los datos sin procesar
        
    Returns:
        list: Datos combinados de todas las fuentes
    """
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


def cargar_datos_bibtex_desde_carpeta(raw_data_path):
    """
    Carga todos los archivos BibTeX de la carpeta data/raw y retorna sus entradas como una lista.
    
    Args:
        raw_data_path (str): Ruta donde se encuentran los archivos BibTeX
        
    Returns:
        list: Lista de entradas BibTeX en formato de diccionario
    """
    combined_data = []
    
    # Buscar todos los archivos .bib o .bibtex en la carpeta
    bibtex_files = glob.glob(os.path.join(raw_data_path, "*.bib")) + \
                   glob.glob(os.path.join(raw_data_path, "*.bibtex"))
    
    if not bibtex_files:
        print(f"No se encontraron archivos BibTeX en {raw_data_path}")
        return combined_data
    
    print(f"\n=== Cargando datos de {len(bibtex_files)} archivos BibTeX encontrados en {raw_data_path} ===")
    
    # Procesar cada archivo BibTeX
    for bibtex_file in bibtex_files:
        print(f"Procesando archivo: {os.path.basename(bibtex_file)}")
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as bibfile:
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = bibtexparser.load(bibfile, parser=parser)
                combined_data += bib_database.entries  # Usar + en lugar de extend
        except UnicodeDecodeError:
            try:
                with open(bibtex_file, 'r', encoding='latin-1') as bibfile:
                    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                    bib_database = bibtexparser.load(bibfile, parser=parser)
                    combined_data += bib_database.entries  # Usar + en lugar de extend
            except Exception as e:
                print(f"Error al procesar {bibtex_file}: {str(e)}")
        except Exception as e:
            print(f"Error al procesar {bibtex_file}: {str(e)}")
    
    print(f"Total de entradas BibTeX cargadas: {len(combined_data)}")
    return combined_data


def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    # Ensure directories exist
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)

    # Ejecutar todos los scrapers con 30 páginas cada uno
    """
    num_pages = 30
    combined_data = ejecutar_scrapers(num_pages, raw_data_path)
    """
    
    # Cargar datos de todos los archivos BibTeX en data/raw
    combined_data = cargar_datos_bibtex_desde_carpeta(raw_data_path)
    
    # Remove duplicates and save unique entries
    unique_file_path = os.path.join(processed_data_path, 'unique_entries.bib')
    duplicates_file_path = os.path.join(processed_data_path, 'duplicates.json')
    unique_entries, duplicates = remove_duplicates_and_save(combined_data, unique_file_path, duplicates_file_path)
    
    # Extract titles for sorting analysis
    titles = [entry.get('title', '') for entry in unique_entries if 'title' in entry]
    
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