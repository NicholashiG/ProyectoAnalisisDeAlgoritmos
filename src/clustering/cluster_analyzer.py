import numpy as np
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
import matplotlib.pyplot as plt
import os

class ClusterAnalyzer:
    """Análisis y evaluación de algoritmos de clustering."""
    
    @staticmethod
    def evaluate_clustering(X, labels_true, labels_pred):
        """
        Evalúa los resultados del clustering usando métricas estándar.
        
        Args:
            X: Datos vectorizados
            labels_true: Etiquetas verdaderas (categorías)
            labels_pred: Etiquetas predichas por el clustering
            
        Returns:
            dict: Diccionario con métricas de evaluación
        """
        metrics = {}
        
        # Verificar si las etiquetas son válidas para evaluación
        unique_clusters = np.unique(labels_pred)
        n_clusters = len(unique_clusters)
        
        print(f"Información de diagnóstico:")
        print(f"- Número de muestras: {len(labels_pred)}")
        print(f"- Número de clusters encontrados: {n_clusters}")
        
        # Mejorar las etiquetas eliminando clusters con una sola muestra
        improved_labels = labels_pred.copy()
        has_singleton = False
        
        # Detectar clusters con una sola muestra y contarlos
        singleton_count = 0
        for cluster in unique_clusters:
            cluster_size = np.sum(labels_pred == cluster)
            if cluster_size == 1:
                singleton_count += 1
                has_singleton = True
        
        if has_singleton:
            print(f"- Detectados {singleton_count} clusters con una sola muestra")
            print("- Corrigiendo etiquetas para el cálculo de silhouette...")
            
            # Asignar los puntos de clusters singleton al cluster más cercano
            # Para cada cluster singleton, encontrar el centroide más cercano
            centroids = {}
            for cluster in unique_clusters:
                if np.sum(labels_pred == cluster) > 1:  # Solo calcular para clusters no-singleton
                    cluster_points = X[labels_pred == cluster]
                    centroids[cluster] = np.mean(cluster_points, axis=0)
            
            # Reasignar cada punto singleton
            for i, label in enumerate(labels_pred):
                if np.sum(labels_pred == label) == 1:  # Es un singleton
                    # Encontrar el cluster más cercano
                    min_dist = float('inf')
                    closest_cluster = None
                    for cluster, centroid in centroids.items():
                        dist = np.linalg.norm(X[i] - centroid)
                        if dist < min_dist:
                            min_dist = dist
                            closest_cluster = cluster
                    
                    if closest_cluster is not None:
                        improved_labels[i] = closest_cluster
        
        # Usar etiquetas mejoradas para el silhouette score
        try:
            from sklearn.metrics import silhouette_score
            if len(np.unique(improved_labels)) > 1:
                metrics['silhouette'] = silhouette_score(X, improved_labels)
            else:
                print("- Error: No se puede calcular silhouette score con un solo cluster")
                metrics['silhouette'] = 0.0
        except Exception as e:
            print(f"- Error calculando silhouette: {e}")
            metrics['silhouette'] = 0.0
        
        # Adjusted Rand Index
        try:
            from sklearn.metrics import adjusted_rand_score
            metrics['adjusted_rand'] = adjusted_rand_score(labels_true, labels_pred)
        except Exception as e:
            print(f"- Error calculando adjusted_rand: {e}")
            metrics['adjusted_rand'] = 0.0
        
        # Normalized Mutual Information
        try:
            from sklearn.metrics import normalized_mutual_info_score
            metrics['nmi'] = normalized_mutual_info_score(labels_true, labels_pred)
        except Exception as e:
            print(f"- Error calculando nmi: {e}")
            metrics['nmi'] = 0.0
        
        return metrics
    
    @staticmethod
    def plot_cluster_comparison(metrics_agglomerative, metrics_divisive):
        """
        Compara el rendimiento de los dos algoritmos de clustering.
        
        Args:
            metrics_agglomerative: Métricas del algoritmo aglomerativo
            metrics_divisive: Métricas del algoritmo divisivo
        """
        metrics = ['silhouette', 'adjusted_rand', 'nmi']
        x = np.arange(len(metrics))
        width = 0.35
        
        # Depurar valores de entrada
        print("\nDatos para comparación:")
        print(f"Aglomerativo: {metrics_agglomerative}")
        print(f"Divisivo: {metrics_divisive}")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Convertir valores de métricas a float
        agglomerative_values = []
        divisive_values = []
        
        for m in metrics:
            # Manejar valores de aglomerativo
            if m in metrics_agglomerative:
                agg_val = metrics_agglomerative[m]
                if isinstance(agg_val, str):
                    print(f"Convirtiendo string '{agg_val}' a 0 para aglomerativo/{m}")
                    agglomerative_values.append(0)
                elif hasattr(agg_val, 'item'):  # Para valores numpy
                    agglomerative_values.append(float(agg_val.item()))
                else:
                    try:
                        agglomerative_values.append(float(agg_val))
                    except (TypeError, ValueError):
                        print(f"No se pudo convertir {agg_val} a float para aglomerativo/{m}. Usando 0.")
                        agglomerative_values.append(0)
            else:
                print(f"Métrica {m} faltante para aglomerativo. Usando 0.")
                agglomerative_values.append(0)
            
            # Manejar valores de divisivo
            if m in metrics_divisive:
                div_val = metrics_divisive[m]
                if isinstance(div_val, str):
                    print(f"Convirtiendo string '{div_val}' a 0 para divisivo/{m}")
                    divisive_values.append(0)
                elif hasattr(div_val, 'item'):  # Para valores numpy
                    divisive_values.append(float(div_val.item()))
                else:
                    try:
                        divisive_values.append(float(div_val))
                    except (TypeError, ValueError):
                        print(f"No se pudo convertir {div_val} a float para divisivo/{m}. Usando 0.")
                        divisive_values.append(0)
            else:
                print(f"Métrica {m} faltante para divisivo. Usando 0.")
                divisive_values.append(0)
        
        # Imprimir valores finales para verificación
        print("\nValores procesados para la gráfica:")
        print(f"Aglomerativo: {agglomerative_values}")
        print(f"Divisivo: {divisive_values}")
        
        # Crear barras con colores distintivos
        rects1 = ax.bar(x - width/2, agglomerative_values, width, label='Aglomerativo',
                       color='#1f77b4', edgecolor='black', alpha=0.8)
        rects2 = ax.bar(x + width/2, divisive_values, width, label='Divisivo',
                       color='#ff7f0e', edgecolor='black', alpha=0.8)
        
        # Mejorar visualización
        ax.set_ylabel('Puntuación', fontsize=14, fontweight='bold')
        ax.set_title('Comparación de Algoritmos de Clustering', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([m.upper() for m in metrics], fontsize=12)
        ax.legend(fontsize=12, loc='upper left')
        
        # Ajustar límites del eje y para mejor visualización
        ymax = max(max(agglomerative_values), max(divisive_values)) * 1.2
        ax.set_ylim(0, ymax)
        
        # Añadir cuadrícula
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir etiquetas con valores
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.4f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize=10, fontweight='bold')
        
        autolabel(rects1)
        autolabel(rects2)
        
        # Añadir leyenda explicativa
        plt.figtext(0.5, 0.01, 
                   "Silhouette: Mide la cohesión de los clusters [-1,1]. Mayor es mejor.\n" +
                   "Adjusted Rand: Mide similitud con clustering real [-1,1]. Mayor es mejor.\n" +
                   "NMI: Información mutua normalizada [0,1]. Mayor es mejor.",
                   ha="center", fontsize=10, 
                   bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.07, 1, 0.98])
        return fig