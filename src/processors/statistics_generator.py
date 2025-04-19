"""
Módulo para generar estadísticas a partir de datos BibTeX procesados.

Este módulo implementa funcionalidades para extraer información estadística
como autores más citados, publicaciones por tipo y año, journals y publishers
con más apariciones en los datos bibliográficos.
"""

import os
import json
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class StatisticsGenerator:
    """
    Genera y analiza estadísticas de datos bibliográficos procesando el archivo BibTeX directamente.
    """
    
    def __init__(self, bibtex_file_path):
        """
        Inicializa el generador de estadísticas.
        
        Args:
            bibtex_file_path (str): Ruta al archivo BibTeX procesado
        """
        self.bibtex_file_path = bibtex_file_path
        
        # Contadores para estadísticas
        self.author_counts = Counter()
        self.journal_counts = Counter()
        self.publisher_counts = Counter()
        self.pubs_by_type_year = {}
        self.entry_count = 0
        
        # Cargar estadísticas directamente desde el archivo
        if bibtex_file_path:
            self.process_bibtex_file()
    
    def process_bibtex_file(self):
        """Procesa el archivo BibTeX directamente, línea por línea."""
        try:
            with open(self.bibtex_file_path, 'r', encoding='utf-8') as bibfile:
                in_entry = False
                current_entry = {}
                current_field = None
                entry_type = None
                
                for line in bibfile:
                    line = line.strip()
                    
                    # Detectar inicio de entrada
                    if line.startswith('@') and '{' in line:
                        in_entry = True
                        self.entry_count += 1
                        
                        # Extraer tipo de entrada
                        entry_type = line.split('{')[0].replace('@', '').strip().lower()
                        current_entry = {'ENTRYTYPE': entry_type}
                        continue
                    
                    # Detectar fin de entrada
                    if in_entry and line == '}':
                        in_entry = False
                        
                        # Procesar la entrada completada para estadísticas
                        self._process_entry_for_stats(current_entry)
                        continue
                    
                    # Procesar campos dentro de la entrada
                    if in_entry and ' = {' in line:
                        parts = line.split(' = {', 1)
                        field = parts[0].strip().lower()
                        value = parts[1]
                        
                        # Si el valor está completo (termina en '},')
                        if value.endswith('},') or value.endswith('}'): 
                            value = value.rstrip(',}')
                            current_entry[field] = value
                        else:
                            # Valor multilinea
                            current_field = field
                            current_entry[field] = value
                        continue
                    
                    # Continuar procesando un valor multilinea
                    if in_entry and current_field:
                        current_entry[current_field] += ' ' + line
                        
                        # Comprobar si llegamos al final del valor
                        if line.endswith('},') or line.endswith('}'): 
                            current_entry[current_field] = current_entry[current_field].rstrip(',}')
                            current_field = None
            
            print(f"Procesados {self.entry_count} registros bibliográficos para análisis.")
            
        except Exception as e:
            print(f"Error al procesar el archivo BibTeX: {str(e)}")
    
    def _process_entry_for_stats(self, entry):
        """Procesa una entrada para actualizar las estadísticas."""
        # Procesar autores
        if 'author' in entry:
            authors = entry['author'].split(' and ')
            authors = [author.strip().replace('{', '').replace('}', '') for author in authors]
            self.author_counts.update(authors)
        
        # Procesar año y tipo
        year_raw = entry.get('year', 'Unknown')
        year_digits = re.search(r'\d{4}', year_raw)
        year = year_digits.group(0) if year_digits else year_raw
        
        entry_type = entry.get('ENTRYTYPE', 'Unknown')
        
        if year not in self.pubs_by_type_year:
            self.pubs_by_type_year[year] = {}
        
        self.pubs_by_type_year[year][entry_type] = self.pubs_by_type_year[year].get(entry_type, 0) + 1
        
        # Procesar journal
        if 'journal' in entry:
            journal = entry['journal'].replace('{', '').replace('}', '').strip()
            self.journal_counts[journal] += 1
        
        # Procesar publisher
        if 'publisher' in entry:
            publisher = entry['publisher'].replace('{', '').replace('}', '').strip()
            self.publisher_counts[publisher] += 1
    
    def get_most_cited_authors(self, limit=15):
        """
        Identifica los autores más citados.
        
        Args:
            limit (int): Cantidad de autores a retornar
            
        Returns:
            list: Lista de tuplas (autor, conteo)
        """
        return self.author_counts.most_common(limit)
    
    def get_publications_by_type_and_year(self):
        """
        Cuenta publicaciones por tipo y año.
        
        Returns:
            dict: Diccionario con estructura {año: {tipo: conteo}}
        """
        return self.pubs_by_type_year
    
    def get_top_journals(self, limit=15):
        """
        Identifica los journals con más apariciones.
        
        Args:
            limit (int): Cantidad de journals a retornar
            
        Returns:
            list: Lista de tuplas (journal, conteo)
        """
        return self.journal_counts.most_common(limit)
    
    def get_top_publishers(self, limit=15):
        """
        Identifica los publishers con más apariciones.
        
        Args:
            limit (int): Cantidad de publishers a retornar
            
        Returns:
            list: Lista de tuplas (publisher, conteo)
        """
        return self.publisher_counts.most_common(limit)
    
    def generate_statistics_report(self, output_folder):
        """
        Genera un informe completo de estadísticas.
        
        Args:
            output_folder (str): Carpeta donde guardar el informe
            
        Returns:
            str: Ruta al archivo de informe generado
        """
        # Crear carpeta si no existe
        os.makedirs(output_folder, exist_ok=True)
        
        # Recopilar todas las estadísticas
        stats = {
            "total_entries": self.entry_count,
            "top_authors": self.get_most_cited_authors(),
            "publications_by_type_year": self.get_publications_by_type_and_year(),
            "top_journals": self.get_top_journals(),
            "top_publishers": self.get_top_publishers()
        }
        
        # Guardar estadísticas en formato JSON
        stats_file_path = os.path.join(output_folder, 'publication_statistics.json')
        with open(stats_file_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
        
        # Generar visualizaciones
        self.generate_visualizations(stats, output_folder)
        
        return stats_file_path
    
    def generate_visualizations(self, stats, output_folder):
        """
        Genera visualizaciones basadas en las estadísticas.
        
        Args:
            stats (dict): Estadísticas recopiladas
            output_folder (str): Carpeta donde guardar las visualizaciones
        """
        # 1. Gráfico de barras para autores más citados
        plt.figure(figsize=(12, 8))
        authors = [author for author, _ in stats["top_authors"]]
        counts = [count for _, count in stats["top_authors"]]
        
        plt.barh(authors[::-1], counts[::-1], color='steelblue')
        plt.xlabel('Cantidad de Citaciones')
        plt.ylabel('Autor')
        plt.title('15 Autores Más Citados')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'top_authors.png'), dpi=300)
        plt.close()
        
        # 2. Gráfico de publicaciones por año y tipo
        pub_by_year = stats["publications_by_type_year"]
        # Ordenar años numéricamente (si es posible)
        try:
            years = sorted([year for year in pub_by_year.keys() if year != 'Unknown'], 
                           key=lambda x: int(x) if x.isdigit() else float('inf'))
            if 'Unknown' in pub_by_year:
                years.append('Unknown')  # Añadir "Unknown" al final
        except ValueError:
            years = sorted(pub_by_year.keys())  # Ordenar alfabéticamente si hay errores

        # Encontrar todos los tipos únicos
        all_types = set()
        for year_data in pub_by_year.values():
            all_types.update(year_data.keys())

        all_types = sorted(all_types)

        # Preparar datos para el gráfico apilado
        data = {entry_type: [] for entry_type in all_types}

        for year in years:
            for entry_type in all_types:
                data[entry_type].append(pub_by_year.get(year, {}).get(entry_type, 0))

        # Crear gráfico apilado
        plt.figure(figsize=(14, 8))
        bottom = np.zeros(len(years))

        # Usar colores distintivos para cada tipo
        colors = plt.cm.tab20(np.linspace(0, 1, len(all_types)))

        for i, entry_type in enumerate(all_types):
            plt.bar(years, data[entry_type], bottom=bottom, label=entry_type, color=colors[i % len(colors)])
            bottom += np.array(data[entry_type])

        plt.xlabel('Año')
        plt.ylabel('Cantidad de Publicaciones')
        plt.title('Publicaciones por Tipo y Año')
        plt.legend(title='Tipo de Publicación', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'publications_by_year_type.png'), dpi=300)
        plt.close()
        
        # 3. Gráfico para journals más frecuentes
        plt.figure(figsize=(12, 8))
        journals = [journal for journal, _ in stats["top_journals"]]
        counts = [count for _, count in stats["top_journals"]]
        
        plt.barh(journals[::-1], counts[::-1], color='forestgreen')
        plt.xlabel('Cantidad de Apariciones')
        plt.ylabel('Journal')
        plt.title('15 Journals con Más Apariciones')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'top_journals.png'), dpi=300)
        plt.close()
        
        # 4. Gráfico para publishers más frecuentes
        plt.figure(figsize=(12, 8))
        publishers = [publisher for publisher, _ in stats["top_publishers"]]
        counts = [count for _, count in stats["top_publishers"]]
        
        plt.barh(publishers[::-1], counts[::-1], color='darkred')
        plt.xlabel('Cantidad de Apariciones')
        plt.ylabel('Editorial')
        plt.title('15 Editoriales con Más Apariciones')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'top_publishers.png'), dpi=300)
        plt.close()


def generate_all_statistics(bibtex_data, output_folder, data_is_file=True):
    """
    Función principal para generar todas las estadísticas.
    
    Args:
        bibtex_data (str): Ruta al archivo BibTeX procesado
        output_folder (str): Carpeta donde guardar los resultados
        data_is_file (bool): Debe ser True para esta versión optimizada
        
    Returns:
        str: Ruta al archivo de informe generado
    """
    if not data_is_file:
        raise ValueError("Esta versión optimizada solo admite procesar archivos BibTeX directamente.")
        
    stats_generator = StatisticsGenerator(bibtex_data)
    report_path = stats_generator.generate_statistics_report(output_folder)
    
    print(f"\nInforme de estadísticas generado en: {report_path}")
    return report_path


if __name__ == "__main__":
    # Ejemplo de uso directo
    from pathlib import Path
    
    # Rutas relativas desde la raíz del proyecto
    root_dir = Path(__file__).resolve().parent.parent.parent
    bibtex_file = os.path.join(root_dir, 'data', 'processed', 'unique_entries.bib')
    output_dir = os.path.join(root_dir, 'data', 'statistics')
    
    generate_all_statistics(bibtex_file, output_dir)