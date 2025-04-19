import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

def save_to_bibtex(entries, output_file):
    """
    Guarda una lista de entradas bibliográficas en formato BibTeX.
    
    Args:
        entries (list): Lista de diccionarios con las entradas bibliográficas
        output_file (str): Ruta del archivo de salida
        
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        # Crear la base de datos BibTeX
        db = BibDatabase()
        db.entries = format_entries(entries)
        
        # Configurar el escritor
        writer = BibTexWriter()
        writer.indent = '    '  # 4 espacios para indentación
        writer.comma_first = False  # Comas al final de línea
        writer.display_order = ['author', 'title', 'booktitle', 'journal', 'year', 
                              'volume', 'number', 'pages', 'doi', 'url', 'publisher']
        
        # Escribir en el archivo
        with open(output_file, 'w', encoding='utf-8') as bibtex_file:
            bibtex_file.write(writer.write(db))
        
        return True
        
    except Exception as e:
        print(f"Error al guardar el archivo BibTeX: {str(e)}")
        return False


def format_entries(entries):
    """
    Formatea y normaliza las entradas BibTeX para asegurar consistencia.
    
    Args:
        entries (list): Lista de diccionarios con entradas bibliográficas
        
    Returns:
        list: Lista de entradas formateadas
    """
    formatted_entries = []
    
    for entry in entries:
        # Crear una copia para no modificar la original
        formatted_entry = entry.copy()
        
        # Asegurar que ID exista y sea único
        if 'ID' not in formatted_entry or not formatted_entry['ID']:
            # Generar ID basado en autor y año si están disponibles
            author_part = formatted_entry.get('author', '').split(',')[0].strip() if 'author' in formatted_entry else 'unknown'
            author_part = author_part.split(' ')[0].lower()  # Primera palabra del primer autor
            year_part = formatted_entry.get('year', 'xxxx')
            formatted_entry['ID'] = f"{author_part}{year_part}"
        
        # Normalizar campos comunes
        for field in ['title', 'journal', 'booktitle', 'publisher']:
            if field in formatted_entry:
                # Añadir llaves para preservar mayúsculas si no las tiene
                value = formatted_entry[field]
                if not (value.startswith('{') and value.endswith('}')):
                    formatted_entry[field] = f"{{{value}}}"
        
        # Asegurar que las páginas tengan formato correcto (usar -- en lugar de -)
        if 'pages' in formatted_entry:
            pages = formatted_entry['pages']
            if '-' in pages and '--' not in pages:
                formatted_entry['pages'] = pages.replace('-', '--')
        
        # Asegurar que el campo 'doi' no contenga la URL completa
        if 'doi' in formatted_entry:
            doi = formatted_entry['doi']
            if doi.startswith('http'):
                # Extraer solo el DOI de la URL
                doi_parts = doi.split('doi.org/')
                if len(doi_parts) > 1:
                    formatted_entry['doi'] = doi_parts[1]
        
        formatted_entries.append(formatted_entry)
    
    return formatted_entries


def merge_bibtex_files(input_files, output_file):
    """
    Combina múltiples archivos BibTeX en uno solo eliminando duplicados.
    
    Args:
        input_files (list): Lista de rutas a archivos BibTeX de entrada
        output_file (str): Ruta del archivo BibTeX de salida
        
    Returns:
        int: Número de entradas en el archivo final
    """
    all_entries = []
    
    # Leer todos los archivos de entrada
    for file_path in input_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = bibtexparser.load(bibtex_file, parser=parser)
                all_entries.extend(bib_database.entries)
        except UnicodeDecodeError:
            # Intentar con codificación alternativa
            with open(file_path, 'r', encoding='latin-1') as bibtex_file:
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = bibtexparser.load(bibtex_file, parser=parser)
                all_entries.extend(bib_database.entries)
    
    # Eliminar duplicados basados en DOI o título
    unique_entries = []
    seen_dois = set()
    seen_titles = set()
    
    for entry in all_entries:
        doi = entry.get('doi', '').lower().strip()
        title = entry.get('title', '').lower().strip()
        
        # Comprobar si es duplicado por DOI o por título
        if (doi and doi in seen_dois) or (title and title in seen_titles):
            continue
            
        # Si no es duplicado, añadirlo a las entradas únicas
        unique_entries.append(entry)
        if doi:
            seen_dois.add(doi)
        if title:
            seen_titles.add(title)
    
    # Guardar el resultado
    save_to_bibtex(unique_entries, output_file)
    
    return len(unique_entries)


def extract_bibtex_info(entries):
    """
    Extrae información resumida de entradas BibTeX.
    
    Args:
        entries (list): Lista de diccionarios con entradas bibliográficas
        
    Returns:
        dict: Estadísticas y metadatos sobre las entradas
    """
    info = {
        'total_entries': len(entries),
        'entry_types': {},
        'years': {},
        'authors': set(),
        'venues': set()
    }
    
    for entry in entries:
        # Contar por tipo de entrada
        entry_type = entry.get('ENTRYTYPE', 'unknown')
        info['entry_types'][entry_type] = info['entry_types'].get(entry_type, 0) + 1
        
        # Contar por año
        if 'year' in entry:
            year = entry['year']
            info['years'][year] = info['years'].get(year, 0) + 1
        
        # Recopilar autores únicos
        if 'author' in entry:
            authors = entry['author'].split(' and ')
            for author in authors:
                info['authors'].add(author.strip())
        
        # Recopilar venues (journals/conferences)
        venue = entry.get('journal', entry.get('booktitle', ''))
        if venue:
            info['venues'].add(venue.strip().replace('{', '').replace('}', ''))
    
    # Convertir sets a listas para serialización
    info['authors'] = list(info['authors'])
    info['venues'] = list(info['venues'])
    
    return info