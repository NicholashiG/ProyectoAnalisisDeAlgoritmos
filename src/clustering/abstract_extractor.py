import os
import re
from collections import defaultdict

class AbstractExtractor:
    """Extrae abstracts de archivos BibTeX."""
    
    def __init__(self):
        """Inicializa el extractor."""
        pass
    
    def extract_from_bibtex(self, bibtex_path):
        """
        Extrae abstracts directamente del archivo BibTeX.
        
        Args:
            bibtex_path: Ruta al archivo BibTeX
            
        Returns:
            Dict: Diccionario con IDs como claves y abstracts como valores
        """
        abstracts = {}
        categories = defaultdict(list)  # Para almacenar categorías (keywords)
        
        try:
            with open(bibtex_path, 'r', encoding='utf-8') as file:
                entry_id = None
                abstract = None
                keywords = None
                in_abstract = False
                in_keywords = False
                
                for line in file:
                    line = line.strip()
                    
                    # Detectar inicio de entrada
                    if line.startswith('@'):
                        entry_id = None
                        abstract = None
                        keywords = None
                        in_abstract = False
                        in_keywords = False
                        
                        # Extraer ID de la entrada
                        if '{' in line:
                            parts = line.split('{', 1)
                            if len(parts) > 1:
                                entry_id = parts[1].split(',')[0].strip()
                    
                    # Detectar abstract
                    elif 'abstract = {' in line and entry_id is not None:
                        in_abstract = True
                        abstract = line.replace('abstract = {', '')
                        
                        # Comprobar si el abstract termina en la misma línea
                        if '},' in abstract:
                            abstract = abstract.split('},')[0]
                            in_abstract = False
                            abstracts[entry_id] = abstract
                    
                    # Continuar leyendo el abstract si estamos en uno
                    elif in_abstract and entry_id is not None:
                        # Comprobar si esta línea finaliza el abstract
                        if '},' in line:
                            abstract += ' ' + line.split('},')[0]
                            in_abstract = False
                            abstracts[entry_id] = abstract
                        else:
                            abstract += ' ' + line
                    
                    # Detectar keywords/categorías
                    elif 'keywords = {' in line and entry_id is not None:
                        in_keywords = True
                        keywords = line.replace('keywords = {', '')
                        
                        # Comprobar si los keywords terminan en la misma línea
                        if '},' in keywords:
                            keywords = keywords.split('},')[0]
                            in_keywords = False
                            if entry_id in abstracts:
                                for kw in keywords.split(','):
                                    kw = kw.strip().lower()
                                    if kw:
                                        categories[kw].append(entry_id)
                    
                    # Continuar leyendo keywords si estamos en ellos
                    elif in_keywords and entry_id is not None:
                        # Comprobar si esta línea finaliza los keywords
                        if '},' in line:
                            keywords += ' ' + line.split('},')[0]
                            in_keywords = False
                            if entry_id in abstracts:
                                for kw in keywords.split(','):
                                    kw = kw.strip().lower()
                                    if kw:
                                        categories[kw].append(entry_id)
                        else:
                            keywords += ' ' + line
                
            print(f"Extraídos {len(abstracts)} abstracts del archivo BibTeX.")
            return abstracts, categories
            
        except Exception as e:
            print(f"Error al extraer abstracts: {e}")
            return {}, {}
    
    def extract_sample(self, abstracts, max_samples=100):
        """
        Extrae una muestra limitada de abstracts para análisis.
        
        Args:
            abstracts: Diccionario completo de abstracts
            max_samples: Número máximo de muestras a extraer
            
        Returns:
            Dict: Subconjunto de abstracts
        """
        sample = {}
        count = 0
        
        # Filtrar abstracts vacíos o muy cortos
        filtered_abstracts = {k: v for k, v in abstracts.items() if isinstance(v, str) and len(v) > 50}
        
        for entry_id, abstract in filtered_abstracts.items():
            sample[entry_id] = abstract
            count += 1
            if count >= max_samples:
                break
                
        return sample