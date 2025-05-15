import os
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from collections import Counter

# Añadir el directorio raíz al path de Python para resolver las importaciones
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importar módulos de clustering
from src.clustering.preprocessor import TextPreprocessor
from src.clustering.abstract_extractor import AbstractExtractor
from src.clustering.agglomerative_clustering import AgglomerativeClustering
from src.clustering.divisive_clustering import DivisiveClusteringGraph
from src.clustering.cluster_analyzer import ClusterAnalyzer

def main():
    # Definir rutas
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    processed_dir = os.path.join(data_dir, 'processed')
    bibtex_path = os.path.join(processed_dir, 'unique_entries.bib')
    output_dir = os.path.join(data_dir, 'clustering_results')
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Iniciando análisis de clustering de abstracts ===")
    
    # Extraer abstracts
    print("Extrayendo abstracts del archivo BibTeX...")
    extractor = AbstractExtractor()
    all_abstracts, categories = extractor.extract_from_bibtex(bibtex_path)
    
    # Tomar una muestra para análisis (ajustar según capacidad computacional)
    sample_size = 1000
    abstracts = extractor.extract_sample(all_abstracts, max_samples=sample_size)
    
    # Preprocesar abstracts
    print(f"Preprocesando {len(abstracts)} abstracts...")
    preprocessor = TextPreprocessor()
    
    # Documentos y sus IDs
    doc_ids = list(abstracts.keys())
    documents = [abstracts[doc_id] for doc_id in doc_ids]
    
    # Preprocesar cada documento
    processed_docs = [preprocessor.preprocess(doc) for doc in documents]
    
    # Guardar los abstracts procesados
    print("Guardando abstracts procesados...")
    abstracts_output = []
    for i, doc_id in enumerate(doc_ids):
        abstracts_output.append({
            "doc_id": doc_id,
            "abstract_original": abstracts[doc_id],
            "abstract_processed": processed_docs[i]
        })

    # Guardar en formato JSON
    import json
    abstracts_processed_path = os.path.join(output_dir, 'processed_abstracts.json')
    with open(abstracts_processed_path, 'w', encoding='utf-8') as f:
        json.dump(abstracts_output, f, indent=2, ensure_ascii=False)

    # Opcionalmente, guardar también en formato CSV para más facilidad de lectura
    import csv
    abstracts_csv_path = os.path.join(output_dir, 'processed_abstracts.csv')
    with open(abstracts_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['doc_id', 'abstract_original', 'abstract_processed'])
        for item in abstracts_output:
            writer.writerow([item['doc_id'], item['abstract_original'], item['abstract_processed']])

    print(f"- Abstracts procesados guardados en: {abstracts_processed_path}")
    print(f"- Abstracts procesados (CSV) guardados en: {abstracts_csv_path}")

    # Vectorizar los documentos usando TF-IDF
    print("Vectorizando documentos...")
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(processed_docs).toarray()
    
    # Preparar etiquetas verdaderas si hay categorías disponibles
    print("Preparando categorías para evaluación...")
    
    # Encontrar la categoría más frecuente para cada documento
    doc_to_category = {}
    for category, docs in categories.items():
        for doc_id in docs:
            if doc_id in doc_ids:
                if doc_id not in doc_to_category:
                    doc_to_category[doc_id] = category
    
    # Mapear categorías a índices numéricos
    unique_categories = list(set(doc_to_category.values()))
    category_to_index = {cat: i for i, cat in enumerate(unique_categories)}
    
    # Crear array de etiquetas verdaderas
    true_labels = np.zeros(len(doc_ids), dtype=int)
    for i, doc_id in enumerate(doc_ids):
        if doc_id in doc_to_category:
            category = doc_to_category[doc_id]
            true_labels[i] = category_to_index.get(category, -1)
    
    # Aplicar algoritmo 1: Clustering Aglomerativo con número fijo de clusters
    print("Ejecutando algoritmo de clustering aglomerativo...")
    agg_clustering = AgglomerativeClustering(linkage='average', n_clusters=20)
    agg_clustering.fit(X)
    
    # Aplicar algoritmo 2: Clustering Divisivo con límite de clusters
    print("Ejecutando algoritmo de clustering divisivo basado en grafos...")
    div_clustering = DivisiveClusteringGraph(threshold=0.15, max_clusters=20)  # Umbral más bajo para incluir más conexiones
    div_clustering.fit(X)
    
    # Evaluar los resultados
    print("Evaluando resultados de clustering...")
    metrics_agg = ClusterAnalyzer.evaluate_clustering(X, true_labels, agg_clustering.labels_)
    metrics_div = ClusterAnalyzer.evaluate_clustering(X, true_labels, div_clustering.labels_)
    
    print("\nResultados de Evaluación:")
    print("Algoritmo Aglomerativo:", metrics_agg)
    print("Algoritmo Divisivo:", metrics_div)
    
    # Generar dendrogramas
    print("Generando visualizaciones...")
    
    # Crear etiquetas abreviadas para visualización
    short_labels = []
    for doc_id in doc_ids:
        doc = abstracts[doc_id][:30].replace('\n', ' ')
        if len(doc) == 30:
            doc += "..."
        short_labels.append(doc)
    
    # Dendrograma del algoritmo aglomerativo
    result_agg = agg_clustering.plot_dendrogram(labels=short_labels)

    if isinstance(result_agg, tuple):
        fig_agg, table_agg = result_agg
        fig_agg_path = os.path.join(output_dir, 'dendrogram_agglomerative.png')
        fig_agg.savefig(fig_agg_path, dpi=300, bbox_inches='tight')
        
        table_agg_path = os.path.join(output_dir, 'dendrogram_agglomerative_table.png')
        table_agg.savefig(table_agg_path, dpi=300, bbox_inches='tight')
    else:
        fig_agg = result_agg
        fig_agg_path = os.path.join(output_dir, 'dendrogram_agglomerative.png')
        fig_agg.savefig(fig_agg_path, dpi=300, bbox_inches='tight')

    # Dendrograma del algoritmo divisivo
    result_div = div_clustering.plot_dendrogram(labels=short_labels)

    # Define paths for divisive visualizations
    fig_div_path = None
    table_div_path = None

    if isinstance(result_div, tuple):
        fig_div, table_div = result_div
        fig_div_path = os.path.join(output_dir, 'dendrogram_divisive.png')
        fig_div.savefig(fig_div_path, dpi=300, bbox_inches='tight')
        
        table_div_path = os.path.join(output_dir, 'dendrogram_divisive_table.png')
        table_div.savefig(table_div_path, dpi=300, bbox_inches='tight')
    else:
        fig_div = result_div
        fig_div_path = os.path.join(output_dir, 'dendrogram_divisive.png')
        fig_div.savefig(fig_div_path, dpi=300, bbox_inches='tight')

    # Comparación de algoritmos
    fig_comp = ClusterAnalyzer.plot_cluster_comparison(metrics_agg, metrics_div)
    fig_comp_path = os.path.join(output_dir, 'clustering_comparison.png')
    fig_comp.savefig(fig_comp_path, dpi=300, bbox_inches='tight')

    print("\nVisualización de resultados guardados en:")
    print(f"- Dendrograma Aglomerativo: {fig_agg_path}")
    if isinstance(result_agg, tuple):
        print(f"- Tabla Aglomerativo: {table_agg_path}")

    if fig_div_path:
        print(f"- Dendrograma Divisivo: {fig_div_path}")
        if table_div_path:
            print(f"- Tabla Divisivo: {table_div_path}")

    print(f"- Comparación de Algoritmos: {fig_comp_path}")
    print("\nAnálisis de clustering completado!")

if __name__ == "__main__":
    main()

"""
El código está limitando intencionalmente el número de abstracts para el análisis debido a las limitaciones computacionales de los algoritmos de clustering jerárquico. En el archivo clustering_analysis.py, hay una línea específica que restringe el número de muestras:

La razón principal para esta limitación es:

Complejidad computacional: Los algoritmos de clustering jerárquico tienen una complejidad de:

Aglomerativo: O(n³) en tiempo y O(n²) en espacio
Divisivo: Puede ser aún más costoso
Recursos necesarios para 12,000 abstracts:

Una matriz de distancias de 12,000 × 12,000 requeriría aproximadamente 1.1 GB solo para almacenar
El tiempo de procesamiento sería extremadamente largo (posiblemente días)
La visualización de un dendrograma con 12,000 hojas sería prácticamente imposible de interpretar
Limitaciones de visualización: Un dendrograma con miles de nodos es visualmente incomprensible y la mayoría de las bibliotecas de visualización tendrían dificultades para renderizarlo.

Si quieres aumentar el número de abstracts para el análisis, puedes modificar el valor de sample_size a un número mayor (por ejemplo, 200 o 500), pero ten en cuenta que:

El tiempo de procesamiento aumentará sustancialmente
La memoria requerida crecerá cuadráticamente con el número de documentos
La visualización podría volverse ilegible o incluso fallar
Para procesar todos los 12,000 abstracts, sería necesario usar enfoques alternativos como:

Algoritmos de clustering más eficientes (BIRCH, HDBSCAN)
Implementaciones distribuidas para clustering jerárquico
Técnicas de reducción de dimensionalidad más agresivas antes del clustering
"""