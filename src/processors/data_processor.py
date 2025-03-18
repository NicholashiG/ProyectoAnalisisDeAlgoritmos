import json
import os
from src.formatters.bibtex_formatter import save_to_bibtex


def remove_duplicates_and_save(data, unique_file_path, duplicates_file_path):
    """Elimina duplicados basados en título y guarda los resultados"""
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
    print(f"Entradas únicas: {len(unique_entries)}")

    # Save duplicates to JSON
    with open(duplicates_file_path, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, indent=4, ensure_ascii=False)
    print(f"Archivo de registros duplicados guardado en: {duplicates_file_path}")
    print(f"Entradas duplicadas: {len(duplicates)}")

    return unique_entries, duplicates