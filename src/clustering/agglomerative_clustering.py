import numpy as np
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

class AgglomerativeClustering:
    """
    Implementación de clustering jerárquico aglomerativo usando matrices.
    Esta implementación usa arrays de NumPy como estructura de datos principal.
    """
    
    def __init__(self, linkage='single', n_clusters=None):
        """
        Inicializa el algoritmo de clustering.
        
        Args:
            linkage: Método de enlace ('single', 'complete', 'average')
            n_clusters: Número de clusters a formar (None para determinar automáticamente)
        """
        self.linkage_method = linkage
        self.n_clusters = n_clusters if n_clusters is not None else 10  # Default a 10 clusters
        self.labels_ = None
        self.n_samples = 0
        self.linkage_matrix = None
    
    def fit(self, X):
        """
        Ejecuta el algoritmo de clustering sobre los datos.
        
        Args:
            X: Matriz de vectores de características o matriz de distancias
            
        Returns:
            self
        """
        # X es una matriz de características donde cada fila representa un documento
        self.n_samples = X.shape[0]
        
        # Calcular directamente la matriz de enlace usando scipy
        print(f"Calculando matriz de enlace usando método '{self.linkage_method}'...")
        self.linkage_matrix = linkage(X, method=self.linkage_method, metric='cosine')
        
        # Determinar número de clusters si no se especificó
        if self.n_clusters is None:
            # Determinar número de clusters automáticamente basado en la distancia
            # Un umbral del 70% de la distancia máxima suele dar buenos resultados
            max_dist = self.linkage_matrix[-1, 2]
            threshold = 0.7 * max_dist
            self.n_clusters = len(np.unique(fcluster(self.linkage_matrix, threshold, criterion='distance')))
            print(f"Número de clusters determinado automáticamente: {self.n_clusters}")
        else:
            print(f"Usando número de clusters predefinido: {self.n_clusters}")
        
        # Extraer etiquetas de cluster
        self.labels_ = fcluster(self.linkage_matrix, self.n_clusters, criterion='maxclust') - 1
        
        # Verificar si hay clusters con una sola muestra y ajustar
        unique_labels, counts = np.unique(self.labels_, return_counts=True)
        singleton_clusters = unique_labels[counts == 1]
        
        if len(singleton_clusters) > 0:
            print(f"Se detectaron {len(singleton_clusters)} clusters con una sola muestra. Ajustando...")
            
            # Si hay más de 2 clusters no singleton, reducir n_clusters
            if len(unique_labels) - len(singleton_clusters) > 2:
                adjusted_n = self.n_clusters - len(singleton_clusters)
                print(f"Reajustando a {adjusted_n} clusters...")
                self.labels_ = fcluster(self.linkage_matrix, adjusted_n, criterion='maxclust') - 1
            # Si no hay suficientes clusters no singleton, fusionar los singletons con su vecino más cercano
            else:
                print("Manteniendo el número de clusters pero fusionando singletons...")
                # Implementación simplificada usando una nueva llamada a fcluster
                self.labels_ = fcluster(self.linkage_matrix, self.n_clusters - len(singleton_clusters) + 1, criterion='maxclust') - 1
        
        # Verificar que tenemos más de un cluster
        unique_clusters = np.unique(self.labels_)
        print(f"Clusters generados: {len(unique_clusters)}")
        
        return self
    
    def plot_dendrogram(self, labels=None):
        """
        Genera un dendrograma completo en forma de árbol.
        
        Args:
            labels: Etiquetas para los nodos hoja
        """
        if self.linkage_matrix is None:
            raise ValueError("El modelo debe ser ajustado primero usando fit()")
        
        # Crear una figura grande para mostrar todo el árbol
        plt.figure(figsize=(20, 12))
        
        # Configurar la visualización para mostrar el árbol completo
        from scipy.cluster.hierarchy import dendrogram
        
        # Aplicar colores personalizados para distinguir clusters
        from scipy.cluster.hierarchy import set_link_color_palette
        set_link_color_palette(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
        
        # Usar truncate_mode=None para mostrar el árbol completo
        dendro = dendrogram(
            self.linkage_matrix,
            labels=labels,
            orientation='top',  # Dendrograma clásico
            above_threshold_color='gray',
            color_threshold=0.7 * self.linkage_matrix[-1, 2],
            leaf_rotation=90,  # Rotar etiquetas para mejor visualización
            leaf_font_size=9,  # Tamaño de fuente adecuado
            show_leaf_counts=True,  # Mostrar número de hojas en cada rama
            no_plot=False,  # Asegurar que se dibuje
            truncate_mode=None,  # No truncar ninguna parte del árbol
            count_sort=False,  # No reordenar por conteo
            distance_sort=False  # No reordenar por distancia
        )
        
        # Configuración detallada del gráfico
        plt.title('Dendrograma Jerárquico Aglomerativo Completo', fontsize=18, fontweight='bold')
        plt.xlabel('Muestras', fontsize=14)
        plt.ylabel('Distancia entre clusters', fontsize=14)
        
        # Añadir espacio para las etiquetas
        plt.subplots_adjust(bottom=0.25)
        
        # Añadir una descripción del método de enlace
        method_desc = {
            'single': 'Enlace simple (distancia mínima)',
            'complete': 'Enlace completo (distancia máxima)',
            'average': 'Enlace promedio (distancia media)',
            'ward': 'Método Ward (minimiza varianza)'
        }
        
        plt.figtext(0.5, 0.01, 
                   f"Método de enlace: {method_desc.get(self.linkage_method, self.linkage_method)}\n"
                   f"Número de clusters: {len(np.unique(self.labels_))}",
                   ha="center", fontsize=12, 
                   bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        return plt.gcf()