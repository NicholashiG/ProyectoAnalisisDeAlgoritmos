import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain
from scipy.spatial.distance import squareform, pdist
import sys

class DivisiveClusteringGraph:
    """
    Implementación de clustering jerárquico divisivo usando grafos.
    Esta implementación usa la librería NetworkX como estructura de datos principal.
    """
    
    def __init__(self, threshold=0.2, max_clusters=20):
        """
        Inicializa el algoritmo de clustering.
        
        Args:
            threshold: Umbral de similitud para conectar nodos
            max_clusters: Número máximo de clusters a crear
        """
        self.threshold = threshold
        self.max_clusters = max_clusters
        self.tree = None
        self.labels_ = None
        self.graph = None
        self.all_samples = None
        self.n_samples = 0
    
    def fit(self, X):
        """
        Ejecuta el algoritmo de clustering sobre los datos.
        
        Args:
            X: Matriz de vectores de características
                
        Returns:
            self
        """
        print("\n=== Ejecutando algoritmo de clustering divisivo revisado ===")
        
        # Almacenar número total de muestras
        self.n_samples = X.shape[0]
        self.all_samples = list(range(self.n_samples))
        print(f"Total de documentos a procesar: {self.n_samples}")
        
        # Calculamos la matriz de similitud basada en distancia coseno
        print("Calculando matriz de similitud...")
        similarity_matrix = 1 - squareform(pdist(X, metric='cosine'))
        
        # Crear grafo con umbral de similitud adaptativo
        print(f"Construyendo grafo con umbral inicial: {self.threshold}")
        self.graph = nx.Graph()
        
        # Añadir todos los nodos
        for i in range(self.n_samples):
            self.graph.add_node(i)
        
        # Primera pasada: añadir aristas con umbral inicial
        edges_added = 0
        connected_nodes = set()
        
        for i in range(self.n_samples):
            for j in range(i+1, self.n_samples):
                if similarity_matrix[i, j] > self.threshold:
                    self.graph.add_edge(i, j, weight=similarity_matrix[i, j])
                    edges_added += 1
                    connected_nodes.add(i)
                    connected_nodes.add(j)
        
        print(f"Aristas añadidas: {edges_added}")
        print(f"Nodos conectados: {len(connected_nodes)}/{self.n_samples}")
        
        # Si hay muchos nodos aislados, reducir el umbral adaptivamente
        if len(connected_nodes) < self.n_samples * 0.8:
            print("Muchos nodos aislados detectados. Ajustando umbral...")
            
            # Reducir umbral hasta conectar al menos el 80% de los nodos
            adaptive_threshold = self.threshold
            while len(connected_nodes) < self.n_samples * 0.8 and adaptive_threshold > 0.05:
                adaptive_threshold -= 0.05
                print(f"Probando umbral: {adaptive_threshold}")
                
                # Limpiar grafo actual
                self.graph = nx.Graph()
                for i in range(self.n_samples):
                    self.graph.add_node(i)
                
                # Añadir aristas con nuevo umbral
                connected_nodes = set()
                edges_added = 0
                
                for i in range(self.n_samples):
                    for j in range(i+1, self.n_samples):
                        if similarity_matrix[i, j] > adaptive_threshold:
                            self.graph.add_edge(i, j, weight=similarity_matrix[i, j])
                            edges_added += 1
                            connected_nodes.add(i)
                            connected_nodes.add(j)
                
                print(f"Con umbral {adaptive_threshold}: {len(connected_nodes)}/{self.n_samples} nodos conectados, {edges_added} aristas")
            
            # Actualizar umbral usado
            self.threshold = adaptive_threshold
            print(f"Umbral final utilizado: {self.threshold}")
        
        # Verificar componentes conectados
        components = list(nx.connected_components(self.graph))
        print(f"Componentes conectados: {len(components)}")
        for i, comp in enumerate(components[:5]):  # Mostrar los primeros 5 componentes
            print(f"  Componente {i}: {len(comp)} nodos")
        
        # Inicializar árbol de clustering
        self.tree = nx.Graph()
        self.tree.add_node("root", samples=self.all_samples)
        
        # Ejecutar clustering divisivo adaptado para garantizar cobertura total
        self._perform_divisive_clustering()
        
        # Después del clustering, verificar si todos los nodos están asignados
        assigned_samples = set()
        leaf_nodes = [node for node, degree in self.tree.degree() if degree == 1 and node != "root"]
        
        for node in leaf_nodes:
            if "samples" in self.tree.nodes[node]:
                assigned_samples.update(self.tree.nodes[node]["samples"])
        
        # Verificar cobertura
        missing_samples = set(self.all_samples) - assigned_samples
        print(f"Verificación de cobertura:")
        print(f"- Muestras asignadas: {len(assigned_samples)}/{self.n_samples}")
        
        if missing_samples:
            print(f"- ADVERTENCIA: {len(missing_samples)} muestras no asignadas")
            # Asignar explícitamente las muestras faltantes
            for sample in missing_samples:
                new_node = f"isolated_{sample}"
                self.tree.add_node(new_node, samples=[sample])
                self.tree.add_edge("root", new_node)
                print(f"  Asignado nodo aislado para muestra {sample}")
        
        # Generar etiquetas de cluster
        self._generate_cluster_labels()
        
        # Verificación final
        unique_labels = np.unique(self.labels_)
        print(f"Clusters generados: {len(unique_labels)}")
        print(f"Documentos etiquetados: {len(self.labels_)}/{self.n_samples}")
        
        # Verificar que no hay valores -1 (sin asignar)
        if -1 in unique_labels:
            print(f"ADVERTENCIA: Hay {np.sum(self.labels_ == -1)} documentos sin asignar (etiqueta -1)")
        
        return self
    
    def _perform_divisive_clustering(self):
        """Ejecuta el algoritmo divisivo garantizando cobertura total"""
        
        # Dividir componentes conectados
        components = list(nx.connected_components(self.graph))
        
        if len(components) == 0:
            print("No hay componentes conectados. Cada documento será su propio cluster.")
            for i in self.all_samples:
                node_name = f"singleton_{i}"
                self.tree.add_node(node_name, samples=[i])
                self.tree.add_edge("root", node_name)
            return
            
        # Si hay múltiples componentes, tratarlos como clusters iniciales
        if len(components) > 1:
            print(f"Procesando {len(components)} componentes como clusters iniciales")
            for i, component in enumerate(components):
                comp_samples = list(component)
                if len(comp_samples) > 0:
                    node_name = f"component_{i}"
                    self.tree.add_node(node_name, samples=comp_samples)
                    self.tree.add_edge("root", node_name)
                    
                    # Subdividir componentes grandes recursivamente
                    if len(comp_samples) > 3:
                        self._subdivide_cluster(node_name, comp_samples)
        else:
            # Si hay un solo componente, dividir recursivamente
            print("Procesando el componente único")
            component = list(components[0])
            
            # Verificar nodos no conectados
            unconnected = set(self.all_samples) - set(component)
            if unconnected:
                print(f"{len(unconnected)} nodos no están en el componente conectado principal")
                # Añadir nodos no conectados como componentes individuales
                for i, node in enumerate(unconnected):
                    node_name = f"isolated_{i}"
                    self.tree.add_node(node_name, samples=[node])
                    self.tree.add_edge("root", node_name)
            
            # Subdividir el componente principal
            if component:
                self._subdivide_cluster("root", component)
        
        # Verificar nodos aislados (que no están en ningún componente)
        all_component_nodes = set()
        for comp in components:
            all_component_nodes.update(comp)
        
        isolated_nodes = set(self.all_samples) - all_component_nodes
        if isolated_nodes:
            print(f"Añadiendo {len(isolated_nodes)} nodos completamente aislados")
            for i, node in enumerate(isolated_nodes):
                node_name = f"isolated_node_{i}"
                self.tree.add_node(node_name, samples=[node])
                self.tree.add_edge("root", node_name)
    
    def _subdivide_cluster(self, node_name, samples, level=0):
        """
        Subdivide un cluster recursivamente.
        
        Args:
            node_name: Nombre del nodo en el árbol
            samples: Lista de índices de muestra en el cluster
            level: Nivel actual de recursión
        """
        if level >= 5:  # Limitar profundidad para evitar explosión
            return
            
        if len(samples) <= 2:  # No dividir clusters muy pequeños
            return
            
        # Extraer subgrafo
        subgraph = self.graph.subgraph(samples).copy()
        
        # Verificar si hay suficientes aristas para dividir
        if len(subgraph.edges()) <= 1:
            return
        
        # Detectar comunidades
        try:
            partition = community_louvain.best_partition(subgraph)
            communities = {}
            for node, community_id in partition.items():
                if community_id not in communities:
                    communities[community_id] = []
                communities[community_id].append(node)
            
            # Convertir a lista de comunidades
            community_list = list(communities.values())
            
            # Si solo hay una comunidad, no dividir más
            if len(community_list) <= 1:
                return
                
            # Añadir subdivisiones al árbol
            for i, community in enumerate(community_list):
                if len(community) > 0:
                    child_name = f"{node_name}_sub{i}"
                    self.tree.add_node(child_name, samples=community)
                    self.tree.add_edge(node_name, child_name)
                    
                    # Recursivamente subdividir
                    self._subdivide_cluster(child_name, community, level + 1)
        except Exception as e:
            print(f"Error al subdividir cluster {node_name}: {e}")
    
    def _generate_cluster_labels(self):
        """Genera etiquetas finales para cada documento basado en el árbol de clustering"""
        
        # Identificar nodos hoja que representan clusters finales
        leaf_nodes = [node for node, degree in self.tree.degree() if degree == 1 and node != "root"]
        
        # Si no hay nodos hoja (solo root), crear uno por documento
        if not leaf_nodes or (len(leaf_nodes) == 1 and len(self.tree.nodes[leaf_nodes[0]]["samples"]) == self.n_samples):
            print("No se pudieron identificar clusters significativos. Asignando cada documento a su propio cluster.")
            self.labels_ = np.arange(self.n_samples)
            return
        
        # Ordenar nodos hoja por tamaño para priorizar clusters grandes
        leaf_sizes = [(node, len(self.tree.nodes[node]["samples"])) for node in leaf_nodes]
        sorted_leaves = sorted(leaf_sizes, key=lambda x: x[1], reverse=True)
        
        # Mostrar distribución de tamaños
        sizes = [size for _, size in sorted_leaves[:10]]
        print(f"Tamaños de los 10 clusters principales: {sizes}")
        
        # Limitar número de clusters si es necesario
        if len(sorted_leaves) > self.max_clusters:
            print(f"Limitando clusters de {len(sorted_leaves)} a {self.max_clusters}")
            
            # Seleccionar los clusters más grandes
            main_clusters = [node for node, _ in sorted_leaves[:self.max_clusters-1]]
            
            # Combinar todos los clusters pequeños en uno
            small_samples = []
            for node, _ in sorted_leaves[self.max_clusters-1:]:
                small_samples.extend(self.tree.nodes[node]["samples"])
            
            # Si hay clusters pequeños combinados, añadirlos
            if small_samples:
                combined_node = "combined_small_clusters"
                self.tree.add_node(combined_node, samples=small_samples)
                self.tree.add_edge("root", combined_node)
                main_clusters.append(combined_node)
                
            final_clusters = main_clusters
        else:
            final_clusters = [node for node, _ in sorted_leaves]
        
        # Inicializar todas las etiquetas a -1 (sin asignar)
        self.labels_ = np.full(self.n_samples, -1)
        
        # Asignar etiquetas a cada documento
        for i, node in enumerate(final_clusters):
            samples = self.tree.nodes[node]["samples"]
            for sample in samples:
                if sample < self.n_samples:  # Verificar índice válido
                    self.labels_[sample] = i
        
        # Verificar si hay documentos sin asignar y asignarlos al cluster más cercano
        unassigned = np.where(self.labels_ == -1)[0]
        if len(unassigned) > 0:
            print(f"Asignando {len(unassigned)} documentos sin etiquetar al cluster más cercano")
            # Para cada documento sin asignar, crear un cluster nuevo
            for i, doc_idx in enumerate(unassigned):
                self.labels_[doc_idx] = len(final_clusters) + i
    
    def plot_dendrogram(self, labels=None):
        """
        Genera una visualización del dendrograma como un grafo jerárquico.
        
        Args:
            labels: Etiquetas para los nodos
        """
        if self.tree is None:
            raise ValueError("El modelo debe ser ajustado primero usando fit()")
        
        # Crear una figura grande
        plt.figure(figsize=(22, 18))
        
        # Verificar nodos en el árbol
        print(f"Visualizando árbol jerárquico con {len(self.tree.nodes())} nodos")
        
        # Usar un layout jerárquico para visualizar claramente la estructura de árbol
        try:
            import pydot
            pos = nx.nx_pydot.graphviz_layout(self.tree, prog="dot", root="root")
            print("Usando layout Graphviz (jerárquico)")
        except:
            # Si falla Graphviz, usar un layout alternativo
            try:
                pos = nx.spring_layout(self.tree, scale=2.0, seed=42)
                print("Usando layout Spring (fuerza dirigida)")
            except:
                # Último recurso: layout jerárquico personalizado
                pos = self._hierarchical_layout()
                print("Usando layout jerárquico personalizado")
        
        # Dividir los nodos por tipo para visualizarlos de manera diferente
        root_node = ["root"] if "root" in self.tree.nodes() else []
        leaf_nodes = [node for node, degree in self.tree.degree() if degree == 1 and node != "root"]
        internal_nodes = [node for node in self.tree.nodes() 
                         if node not in leaf_nodes and node not in root_node]
        
        # Dibujar las aristas primero con un estilo claro
        nx.draw_networkx_edges(
            self.tree, pos,
            width=1.2,
            alpha=0.7,
            edge_color="gray",
            style="solid",
            arrows=False
        )
        
        # Dibujar nodos internos
        nx.draw_networkx_nodes(
            self.tree, pos,
            nodelist=internal_nodes,
            node_size=180,
            node_color="cornflowerblue",
            alpha=0.8,
            edgecolors="black",
            linewidths=0.5
        )
        
        # Dibujar el nodo raíz con un estilo destacado
        if root_node:
            nx.draw_networkx_nodes(
                self.tree, pos,
                nodelist=root_node,
                node_size=400,
                node_color="forestgreen",
                alpha=0.9,
                edgecolors="black",
                linewidths=1.5
            )
        
        # Dibujar nodos hoja (los clusters finales)
        nx.draw_networkx_nodes(
            self.tree, pos,
            nodelist=leaf_nodes,
            node_size=250,
            node_color="tomato",
            alpha=0.8,
            edgecolors="black",
            linewidths=0.5
        )
        
        # Crear etiquetas que informen sobre el tamaño del cluster
        node_labels = {}
        for node in self.tree.nodes():
            if node in leaf_nodes:
                n_samples = len(self.tree.nodes[node]["samples"])
                node_labels[node] = f"{n_samples}"
            elif node in internal_nodes:
                if len(internal_nodes) < 50:  # Solo etiquetar internos si no hay demasiados
                    n_samples = len(self.tree.nodes[node]["samples"])
                    node_labels[node] = f"{n_samples}"
            elif node in root_node:
                n_samples = len(self.tree.nodes[node]["samples"])
                node_labels[node] = f"Root ({n_samples})"
        
        # Añadir etiquetas con formato legible
        nx.draw_networkx_labels(
            self.tree, pos,
            labels=node_labels,
            font_size=9,
            font_weight='bold',
            font_color='black',
            bbox=dict(facecolor="white", edgecolor="gray", boxstyle="round,pad=0.3", alpha=0.7)
        )
        
        # Añadir una leyenda para explicar los colores
        plt.plot([0], [0], 'o', color='forestgreen', markersize=15, label='Raíz')
        plt.plot([0], [0], 'o', color='cornflowerblue', markersize=10, label='Nodos Internos')
        plt.plot([0], [0], 'o', color='tomato', markersize=10, label='Nodos Hoja (Clusters)')
        plt.legend(loc='upper left', frameon=True, fontsize=12)
        
        # Añadir títulos y ajustes
        plt.title('Dendrograma Jerárquico Divisivo', fontsize=18, fontweight='bold')
        plt.text(0.5, 0.02, 
                 "Los números indican la cantidad de documentos en cada nodo.\n"
                 "La estructura muestra cómo se dividen los documentos jerárquicamente.",
                 transform=plt.gcf().transFigure, ha='center', fontsize=12)
        
        # Eliminar ejes para mejor visualización
        plt.axis('off')
        
        # Ajustar límites para que quepa todo el gráfico
        plt.tight_layout(pad=1.5)
        
        return plt.gcf()

    def _hierarchical_layout(self):
        """Layout jerárquico personalizado para visualizar el árbol de manera estructurada"""
        G = self.tree
        pos = {}
        
        # Primero colocar la raíz en la parte superior
        pos["root"] = np.array([0, 1])
        
        # Realizar un recorrido en anchura (BFS) para asignar niveles
        seen = {"root"}
        current_level = ["root"]
        next_level = []
        level_count = 0
        
        while current_level:
            # Calcular ancho para el nivel actual
            level_width = 2.0**level_count
            
            # Posicionar nodos en el nivel actual
            for i, node in enumerate(current_level):
                # Distribuir horizontalmente
                x = (i - len(current_level)/2 + 0.5) * (2.0 / level_width)
                y = 1.0 - (level_count * 0.2)
                pos[node] = np.array([x, y])
                
                # Añadir hijos al siguiente nivel
                for child in G.neighbors(node):
                    if child not in seen:
                        seen.add(child)
                        next_level.append(child)
            
            # Preparar para el siguiente nivel
            current_level = next_level
            next_level = []
            level_count += 1
        
        return pos