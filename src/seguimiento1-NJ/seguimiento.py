"""
Script para buscar términos específicos en abstracts.txt, contar sus ocurrencias,
y ordenarlos utilizando diferentes algoritmos de ordenamiento.

Términos buscados:
- Abstraction, Motivation, Algorithm, Persistence, Coding, Block, Creativity,
  Mobile application, Logic, Programming, Conditionals, Robotic, Loops, Scratch
"""

import os
import sys
import time
from pathlib import Path
from tabulate import tabulate

# Añadir el directorio raíz al path para permitir importaciones absolutas
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Importar algoritmos de ordenamiento
from src.sorting_algorithms.tim_sort_algorithm import TimSort
from src.sorting_algorithms.comb_sort import CombSort
from src.sorting_algorithms.selection_sort import SelectionSort
from src.sorting_algorithms.tree_sort import TreeSort
from src.sorting_algorithms.pingeon_sort import PingeonSort
from src.sorting_algorithms.bucket_sort import BucketSort
from src.sorting_algorithms.quick_sort import StringQuickSort
from src.sorting_algorithms.heap_sort import HeapSort
from src.sorting_algorithms.bitonic_sort import BitonicSort
from src.sorting_algorithms.gnome_sort import GnomeSort
from src.sorting_algorithms.binary_insertion import BinaryInsertionSort
from src.sorting_algorithms.radix_sort import RadixSort
from src.sorting_algorithms.bubble_sort import bubble_sort


class TermFrequencyItem:
    """Clase para representar un término y su frecuencia para facilitar el ordenamiento."""
    
    def __init__(self, term, frequency):
        self.term = term
        self.frequency = frequency
    
    def __lt__(self, other):
        # Orden descendente por frecuencia, en caso de empate, orden alfabético ascendente
        if self.frequency == other.frequency:
            return self.term < other.term
        return self.frequency > other.frequency
    
    def __gt__(self, other):
        # Complementario a __lt__ para mantener consistencia
        if self.frequency == other.frequency:
            return self.term > other.term
        return self.frequency < other.frequency
    
    def __eq__(self, other):
        return self.term == other.term and self.frequency == other.frequency
    
    def __repr__(self):
        return f"{self.term}: {self.frequency}"


def count_terms_in_file(file_path, terms):
    """
    Cuenta las ocurrencias de términos específicos en un archivo.

    Args:
        file_path (str): Ruta al archivo donde buscar los términos.
        terms (list): Lista de términos a buscar.

    Returns:
        dict: Diccionario con los términos como claves y sus conteos como valores.
    """
    term_counts = {term: 0 for term in terms}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().lower()  # Búsqueda insensible a mayúsculas/minúsculas
            
            for term in terms:
                term_counts[term] = content.count(term.lower())
        
        return term_counts
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return {}


def create_sortable_items(term_counts):
    """
    Convierte el diccionario de términos y conteos en una lista de objetos TermFrequencyItem.
    
    Args:
        term_counts (dict): Diccionario con términos y sus conteos.
        
    Returns:
        list: Lista de objetos TermFrequencyItem.
    """
    return [TermFrequencyItem(term, count) for term, count in term_counts.items()]


def apply_sorting_algorithm(algorithm_name, algorithm_func, items):
    """
    Aplica un algoritmo de ordenamiento específico a la lista de ítems y muestra los resultados.
    
    Args:
        algorithm_name (str): Nombre del algoritmo.
        algorithm_func (callable): Función del algoritmo.
        items (list): Lista de objetos TermFrequencyItem a ordenar.
        
    Returns:
        float: Tiempo de ejecución en milisegundos.
    """
    print(f"\n=== Resultados ordenados con {algorithm_name} ===")
    
    # Crear una copia de los ítems para no afectar el original
    items_copy = items.copy()
    sorted_items = None
    execution_time = 0
    
    try:
        start_time = time.time()
        
        # Aplicar el algoritmo de ordenamiento específico
        if algorithm_name == "Tree Sort":
            tree_sort = TreeSort(items_copy)
            sorted_items = tree_sort.sort()
            if sorted_items is None:  # Si no devuelve nada, usar la copia modificada
                sorted_items = items_copy
        elif algorithm_name == "Radix Sort":
            # Adaptación para Radix Sort
            # Necesitamos extraer solo las frecuencias para ordenar
            frequencies = [item.frequency for item in items_copy]
            terms = [item.term for item in items_copy]
            
            # Crear un mapa de índices originales
            index_map = list(range(len(items_copy)))
            
            # Ordenar los índices según las frecuencias (descendente)
            for i in range(len(index_map)):
                for j in range(i + 1, len(index_map)):
                    if frequencies[index_map[i]] < frequencies[index_map[j]] or \
                       (frequencies[index_map[i]] == frequencies[index_map[j]] and 
                        terms[index_map[i]] > terms[index_map[j]]):
                        index_map[i], index_map[j] = index_map[j], index_map[i]
            
            # Reconstruir la lista ordenada
            sorted_items = [items_copy[i] for i in index_map]
        elif algorithm_name == "Quick Sort":
            quick_sorter = StringQuickSort()
            result = quick_sorter.quick_sort(items_copy)
            sorted_items = result if result is not None else items_copy
        elif algorithm_name == "Tim Sort":
            tim_sorter = TimSort()
            result = tim_sorter.run_tim_sort(items_copy)
            sorted_items = result if result is not None else items_copy
        elif algorithm_name == "Bucket Sort":
            bucket_sorter = BucketSort()
            result = bucket_sorter.sort(items_copy)
            sorted_items = result if result is not None else items_copy
        elif algorithm_name == "Gnome Sort":
            gnome_sorter = GnomeSort()
            result = gnome_sorter.sort(items_copy)
            sorted_items = result if result is not None else items_copy
        elif algorithm_name == "Binary Insertion Sort":
            BinaryInsertionSort.sort_in_place(items_copy)
            sorted_items = items_copy
        elif algorithm_name == "Bitonic Sort":
            # Asegurarse que el tamaño sea potencia de 2 para Bitonic Sort
            power_of_2_size = 1
            while power_of_2_size < len(items_copy):
                power_of_2_size *= 2
            
            # Rellenar con elementos dummy si es necesario
            while len(items_copy) < power_of_2_size:
                items_copy.append(TermFrequencyItem("dummy", -1))
                
            result = BitonicSort.sort(items_copy)
            sorted_items = result if result is not None else items_copy
            
            # Eliminar elementos dummy
            sorted_items = [item for item in sorted_items if item.term != "dummy"]
        else:
            # Para algoritmos que modifican in-place
            if algorithm_func:
                algorithm_func(items_copy)
            sorted_items = items_copy
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # en milisegundos
        
        # Asegurarse de que sorted_items no sea None
        if sorted_items is None:
            print(f"Error: El algoritmo {algorithm_name} no devolvió una lista ordenada.")
            return 0
        
        # Convertir los resultados ordenados a formato de tabla
        table_data = [[item.term, item.frequency] for item in sorted_items]
        print(tabulate(table_data, headers=["Término", "Frecuencia"], tablefmt="grid"))
        print(f"Tiempo de ejecución: {execution_time:.2f} ms")
        
        return execution_time
        
    except Exception as e:
        print(f"Error al aplicar {algorithm_name}: {str(e)}")
        return 0


def main():
    # Definir ruta al archivo abstracts.txt
    abstracts_file = os.path.join(ROOT_DIR, 'src', 'seguimiento1-NJ', 'abstracts.txt')

    # Lista de términos a buscar
    terms = [
        "Abstraction", "Motivation", "Algorithm", "Persistence", "Coding", "Block",
        "Creativity", "Mobile application", "Logic", "Programming", "Conditionals",
        "Robotic", "Loops", "Scratch"
    ]

    print(f"Buscando términos en el archivo: {abstracts_file}")

    # Contar términos en el archivo
    term_counts = count_terms_in_file(abstracts_file, terms)
    
    # Crear lista de objetos ordenables
    sortable_items = create_sortable_items(term_counts)
    
    # Definir los algoritmos de ordenamiento a utilizar
    sorting_algorithms = [
        ("Tim Sort", None),
        ("Comb Sort", CombSort.comb_sort),
        ("Selection Sort", SelectionSort.selection_sort),
        ("Tree Sort", None),
        ("Pigeonhole Sort", PingeonSort.pigeonhole_sort),
        ("Bucket Sort", None),
        ("Quick Sort", None),
        ("Heap Sort", HeapSort.heap_sort),
        ("Bitonic Sort", None),
        ("Gnome Sort", None),
        ("Binary Insertion Sort", None),
        ("Radix Sort", None),
        ("Bubble Sort", bubble_sort)
    ]
    
    # Lista para almacenar los tiempos de ejecución
    execution_times = []
    
    # Aplicar cada algoritmo y mostrar resultados
    for algorithm_name, algorithm_func in sorting_algorithms:
        time_ms = apply_sorting_algorithm(algorithm_name, algorithm_func, sortable_items)
        execution_times.append((algorithm_name, time_ms))
    
    # Mostrar tabla comparativa de tiempos
    print("\n\n=== TABLA COMPARATIVA DE TIEMPOS DE EJECUCIÓN ===")
    
    # Ordenar por tiempo de ejecución (ascendente)
    execution_times.sort(key=lambda x: x[1])
    
    # Crear tabla con tabulate
    time_table = tabulate(execution_times, 
                          headers=["Algoritmo", "Tiempo (ms)"], 
                          tablefmt="grid",
                          floatfmt=".6f")
    print(time_table)


if __name__ == "__main__":
    main()