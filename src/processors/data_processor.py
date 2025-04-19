def remove_duplicates_and_save(data, unique_file_path, duplicates_file_path):
    """
    Elimina duplicados de los datos y guarda las entradas únicas y duplicadas en archivos separados.
    
    Args:
        data (list): Lista de entradas BibTeX en formato de diccionario
        unique_file_path (str): Ruta donde guardar las entradas únicas en formato BibTeX
        duplicates_file_path (str): Ruta donde guardar las entradas duplicadas en formato JSON
        
    Returns:
        tuple: (lista de entradas únicas, diccionario de duplicados)
    """
    unique_entries = []
    duplicate_groups = {}
    
    # Usar estos campos para identificar duplicados
    # Prioridad: DOI > título > combinación de autor y año
    encountered_dois = {}
    encountered_titles = {}
    encountered_author_year = {}
    
    print(f"\n=== Eliminando duplicados de {len(data)} entradas ===")
    
    for entry in data:
        # Normalizar los campos para comparación
        entry_id = entry.get('ID', '').strip()
        doi = entry.get('doi', '').strip().lower()
        title = entry.get('title', '').strip().lower()
        # Eliminar caracteres especiales comunes en títulos BibTeX
        title = title.replace('{', '').replace('}', '').replace('\\', '')
        
        # Preparar combinación autor-año como fallback
        author = entry.get('author', '').strip().lower()
        year = entry.get('year', '').strip()
        author_year = f"{author}_{year}" if author and year else None
        
        # Comprobar si es duplicado por DOI
        if doi and doi in encountered_dois:
            duplicate_id = encountered_dois[doi]
            if duplicate_id not in duplicate_groups:
                duplicate_groups[duplicate_id] = [next(e for e in unique_entries if e.get('ID') == duplicate_id)]
            duplicate_groups[duplicate_id].append(entry)
            continue
            
        # Comprobar si es duplicado por título
        elif title and title in encountered_titles:
            duplicate_id = encountered_titles[title]
            if duplicate_id not in duplicate_groups:
                duplicate_groups[duplicate_id] = [next(e for e in unique_entries if e.get('ID') == duplicate_id)]
            duplicate_groups[duplicate_id].append(entry)
            continue
            
        # Comprobar si es duplicado por autor-año
        elif author_year and author_year in encountered_author_year:
            duplicate_id = encountered_author_year[author_year]
            if duplicate_id not in duplicate_groups:
                duplicate_groups[duplicate_id] = [next(e for e in unique_entries if e.get('ID') == duplicate_id)]
            duplicate_groups[duplicate_id].append(entry)
            continue
            
        # Si no es duplicado, añadir a entradas únicas
        unique_entries.append(entry)
        if doi:
            encountered_dois[doi] = entry_id
        if title:
            encountered_titles[title] = entry_id
        if author_year:
            encountered_author_year[author_year] = entry_id
    
    # Guardar entradas únicas en formato BibTeX
    if unique_entries:
        from src.formatters.bibtex_formatter import save_to_bibtex
        save_to_bibtex(unique_entries, unique_file_path)
        print(f"Se guardaron {len(unique_entries)} entradas únicas en {unique_file_path}")
    
    # Convertir grupos de duplicados a formato más amigable para JSON
    duplicates_json = {}
    for key, group in duplicate_groups.items():
        duplicates_json[key] = [{'ID': e.get('ID', ''), 
                                'title': e.get('title', ''),
                                'author': e.get('author', ''),
                                'year': e.get('year', ''), 
                                'doi': e.get('doi', '')} for e in group]
    
    # Guardar duplicados en formato JSON
    if duplicates_json:
        import json
        with open(duplicates_file_path, 'w', encoding='utf-8') as f:
            json.dump(duplicates_json, f, indent=4, ensure_ascii=False)
        print(f"Se guardaron {len(duplicates_json)} grupos de duplicados en {duplicates_file_path}")
    
    print(f"Proceso de eliminación de duplicados completado: {len(unique_entries)} entradas únicas y {len(duplicate_groups)} duplicados identificados")
    
    return unique_entries, duplicate_groups