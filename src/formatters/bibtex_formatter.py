import re
import hashlib
import pybtex.database
from pybtex.database.output import bibtex as bibtex_output


def clean_text(text):
    """Elimina caracteres especiales que pueden causar problemas en BibTeX"""
    # Reemplazar caracteres especiales
    text = re.sub(r'[\\{}]', '', text)
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    return text


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
        # Limpiar los campos para evitar errores de formato
        clean_title = clean_text(entry['title'])
        clean_author = clean_text(entry['author'])
        clean_abstract = clean_text(entry['abstract'])
        clean_year = clean_text(entry['year'])

        fields = {
            'title': clean_title,
            'author': clean_author,
            'year': clean_year,
            'abstract': clean_abstract
        }

        # Eliminar campos vacíos
        fields = {k: v for k, v in fields.items() if v and v.strip()}

        bib_entry = pybtex.database.Entry('article', fields=fields)
        entry_id = generate_safe_bibtex_id(clean_title, clean_author)
        bib_data.entries[entry_id] = bib_entry

    writer = bibtex_output.Writer()
    with open(file_path, 'w', encoding='utf-8') as bibfile:
        writer.write_stream(bib_data, bibfile)

    print(f"Archivo BibTeX guardado en: {file_path}")
    print(f"Total de entradas guardadas: {len(data)}")