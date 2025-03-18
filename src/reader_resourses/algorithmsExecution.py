import time
from src.sorting_algorithms.binary_insertion import BinaryInsertionSort
from src.sorting_algorithms.bitonic_sort import BitonicSort
from src.sorting_algorithms.bucket_sort import BucketSort
from src.sorting_algorithms.comb_sort import CombSort
from src.sorting_algorithms.gnome_sort import GnomeSort
from src.sorting_algorithms.heap_sort import HeapSort
from src.sorting_algorithms.pingeon_sort import PingeonSort
from src.sorting_algorithms.quick_sort import StringQuickSort
from src.sorting_algorithms.radix_sort import RadixSort
from src.sorting_algorithms.selection_sort import SelectionSort
from src.sorting_algorithms.tim_sort_algorithm import TimSort
from src.sorting_algorithms.tree_sort import TreeSort


class AlgorithmsExecution:
    """
    A class that executes the different sorting algorithms for the article titles array.
    """

    @staticmethod
    def run_algorithm(algorithm, arr):
        """
        Run a specific sorting algorithm and measure its execution time.
        """
        try:
            arr_copy = arr.copy()  # Work with a copy to avoid modifying the original array
            start_time = time.time()
            algorithm(arr_copy)
            end_time = time.time()
            exec_time = (end_time - start_time) * 1000  # Convert to milliseconds
            return exec_time
        except Exception as e:
            print(f"Error executing {algorithm.__name__}: {e}")
            return -1

    @staticmethod
    def execute_algorithms(data, data_type):
        """
        Execute all sorting algorithms on the given data and return a table of results.
        """
        algorithms = [
            ("TimSort", TimSort().run_tim_sort),
            ("CombSort", CombSort.comb_sort),
            ("SelectionSort", SelectionSort.selection_sort),
            ("TreeSort", lambda arr: TreeSort(arr).sort()),  # Corrección para TreeSort
            ("PigeonholeSort", PingeonSort.pigeonhole_sort),
            ("BucketSort", BucketSort().sort),
            ("QuickSort", StringQuickSort().quick_sort),
            ("HeapSort", HeapSort.heap_sort),
            ("BitonicSort", BitonicSort.sort),
            ("GnomeSort", GnomeSort().sort),
            ("BinaryInsertionSort", BinaryInsertionSort.sort_in_place),
            ("RadixSort", lambda arr: RadixSort(arr).sort())  # Corrección para RadixSort
        ]

        results = []
        for name, algorithm in algorithms:
            time_taken = AlgorithmsExecution.run_algorithm(algorithm, data)
            if time_taken != -1:
                results.append({
                    "Método de ordenamiento": name,
                    "Tamaño": len(data),
                    "Tiempo (ms)": time_taken
                })

        # Print results in a table format
        print(f"\n=== Resultados para {data_type} ===")
        print("{:<20} {:<10} {:<15}".format("Método", "Tamaño", "Tiempo (ms)"))
        for result in results:
            print("{:<20} {:<10} {:<15.2f}".format(
                result["Método de ordenamiento"],
                result["Tamaño"],
                result["Tiempo (ms)"]
            ))

        return results