import re
import hashlib
import pybtex.database
from pybtex.database.output import bibtex as bibtex_output

def generate_safe_bibtex_id(title, author):
    """Genera un ID BibTeX seguro basado en el título y autor"""
    # Crear un hash corto pero único basado en título y autor
    hash_input = (title + author).encode('utf-8')
    hash_id = hashlib.md5(hash_input).hexdigest()[:8]
    
    # Crear un prefijo con el primer autor y año si está disponible
    prefix = ""
    if author and "," in author:
        first_author = author.split(",")[0].strip()
        # Tomar solo el apellido si hay múltiples nombres
        if " " in first_author:
            prefix = first_author.split()[-1]
        else:
            prefix = first_author
    
    # Eliminar caracteres no válidos y convertir a minúsculas
    if prefix:
        prefix = re.sub(r'[^\w]', '', prefix).lower()
        return f"{prefix}_{hash_id}"
    else:
        return f"entry_{hash_id}"

def save_to_bibtex(data, file_path):
    """Guarda los datos extraídos en formato BibTeX"""
    bib_data = pybtex.database.BibliographyData()
    for entry in data:
        fields = {
            'title': entry['title'],
            'author': entry['author'],
            'year': entry['year'],
            'abstract': entry['abstract']
        }
        bib_entry = pybtex.database.Entry('article', fields=fields)
        entry_id = generate_safe_bibtex_id(entry['title'], entry['author'])
        bib_data.entries[entry_id] = bib_entry
    
    writer = bibtex_output.Writer()
    with open(file_path, 'w', encoding='utf-8') as bibfile:
        writer.write_stream(bib_data, bibfile)
    
    print(f"Archivo BibTeX guardado en: {file_path}")