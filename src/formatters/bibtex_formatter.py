import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import hashlib
import re

def clean_text(text):
    """Elimina caracteres especiales que pueden causar problemas"""
    if not text:
        return ""
    # Reemplazar caracteres especiales
    text = re.sub(r'[\\{}]', '', text)
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_safe_bibtex_id(title, author):
    """Genera un ID BibTeX seguro basado en el título y autor"""
    if not title:
        title = "untitled"
    if not author:
        author = "unknown"

    # Crear un hash corto pero único basado en título y autor
    hash_input = (title + author).encode('utf-8')
    hash_id = hashlib.md5(hash_input).hexdigest()[:8]

    # Crear un prefijo con el primer autor
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
    return f"entry_{hash_id}"

def save_to_bibtex(data, file_path):
    """Guarda los datos extraídos en formato BibTeX usando bibtexparser"""
    db = BibDatabase()
    db.entries = []

    for entry in data:
        # Limpiar y validar los campos
        clean_entry = {
            'title': clean_text(entry.get('title', '')),
            'author': clean_text(entry.get('author', '')),
            'year': clean_text(entry.get('year', '')),
            'abstract': clean_text(entry.get('abstract', '')),
            'ENTRYTYPE': 'article'
        }

        # Generar ID único
        entry_id = generate_safe_bibtex_id(clean_entry['title'], clean_entry['author'])
        clean_entry['ID'] = entry_id

        # Eliminar campos vacíos
        clean_entry = {k: v for k, v in clean_entry.items() if v and v.strip()}

        db.entries.append(clean_entry)

    # Configurar writer para mantener el orden y formato consistente
    writer = BibTexWriter()
    writer.indent = '    '  # 4 espacios
    writer.comma_first = False
    writer.order_entries_by = None  # Mantener orden original

    with open(file_path, 'w', encoding='utf-8') as bibfile:
        bibfile.write(writer.write(db))

    print(f"Archivo BibTeX guardado en: {file_path}")
    print(f"Total de entradas guardadas: {len(data)}")