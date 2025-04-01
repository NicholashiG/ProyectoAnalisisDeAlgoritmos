"""
Script para extraer los abstracts de los artículos y guardarlos en un archivo de texto.

Este script lee el archivo BibTeX procesado (unique_entries.bib) y extrae los abstracts
de cada entrada, guardándolos en un archivo de texto dentro de la carpeta de seguimiento.
"""

import os
import re
from pathlib import Path

def extractor_abstracts(bibtex_file_path):
    """
    Extrae los abstracts de un archivo BibTeX.
    
    Args:
        bibtex_file_path (str): Ruta al archivo BibTeX.
        
    Returns:
        list: Lista de diccionarios con el título y abstract de cada entrada.
    """
    abstracts = []
    
    try:
        with open(bibtex_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Dividir el contenido en entradas individuales
            entries = re.split(r'@\w+{', content)
            
            for entry in entries:
                if not entry.strip():
                    continue
                    
                # Extraer título
                title_match = re.search(r'title\s*=\s*{([^}]+)}', entry)
                title = title_match.group(1) if title_match else "Título no disponible"
                
                # Extraer abstract
                abstract_match = re.search(r'abstract\s*=\s*{([^}]+)}', entry)
                abstract = abstract_match.group(1) if abstract_match else "Abstract no disponible"
                
                if abstract != "Abstract no disponible":
                    abstracts.append({
                        'title': title,
                        'abstract': abstract
                    })
        
        print(f"Se encontraron {len(abstracts)} abstracts en el archivo BibTeX.")
        return abstracts
        
    except Exception as e:
        print(f"Error al leer el archivo BibTeX: {e}")
        return []

def save_abstracts_to_file(abstracts, output_file_path):
    """
    Guarda los abstracts extraídos en un archivo de texto.
    
    Args:
        abstracts (list): Lista de diccionarios con título y abstract.
        output_file_path (str): Ruta donde guardar el archivo de texto.
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write("# ABSTRACTS DE ARTÍCULOS ACADÉMICOS\n\n")
            
            for i, entry in enumerate(abstracts, 1):
                file.write(f"## {i}. {entry['title']}\n\n")
                file.write(f"{entry['abstract']}\n\n")
                file.write("-" * 80 + "\n\n")
        
        print(f"Abstracts guardados exitosamente en: {output_file_path}")
        
    except Exception as e:
        print(f"Error al guardar los abstracts: {e}")

def main():
    # Definir rutas
    root_dir = Path(__file__).resolve().parent.parent.parent
    bibtex_file = os.path.join(root_dir, 'data', 'processed', 'unique_entries.bib')
    output_dir = os.path.join(root_dir, 'src', 'seguimiento1-NJ')
    output_file = os.path.join(output_dir, 'abstracts.txt')
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Leyendo archivo BibTeX: {bibtex_file}")
    
    # Extraer abstracts
    abstracts = extractor_abstracts(bibtex_file)
    
    # Guardar abstracts en archivo de texto
    if abstracts:
        save_abstracts_to_file(abstracts, output_file)
    else:
        print("No se encontraron abstracts para guardar.")

if __name__ == "__main__":
    main()