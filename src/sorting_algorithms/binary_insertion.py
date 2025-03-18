"""
Binary Insertion Sort
Explicación:
Este algoritmo tiene una mejora respecto al de inserción, ya que en lugar de comparar
elemento por elemento, utiliza una búsqueda binaria para encontrar la posición correcta
del elemento en el array

En principio, el algoritmo selecciona un elemento y usa la búsqueda binaria para obtener el 
indice donde se debe insertar el elemento
Para insertar el elemento, se desplazan los elementos a la derecha para hacer espacio
y se inserta el elemento en la posición correcta

Se repite el proceso con cada elemento de la lista

Precauciones:
No es recomendable para listas muy grandes, ya que la búsqueda binaria puede ser costosa 
además que el desplaamiento de elementos puede ser también costoso


"""


class BinaryInsertionSort:
    """
    A class that implements the Binary Insertion Sort algorithm.
    """

    @staticmethod
    def binary_search(arr, item, low, high):
        """
        Binary search method for binary insertion sort.
        """
        while low < high:
            mid = (low + high) // 2
            if arr[mid] < item:
                low = mid + 1
            else:
                high = mid
        return low

    @staticmethod
    def sort(arr):
        """
        Binary insertion sort algorithm implementation.
        Returns a new sorted array.
        """
        arr_copy = arr.copy()
        BinaryInsertionSort.sort_in_place(arr_copy)
        return arr_copy

    @staticmethod
    def sort_in_place(arr):
        """
        Binary insertion sort algorithm implementation that sorts the array in place.
        """
        for i in range(1, len(arr)):
            key = arr[i]
            j = BinaryInsertionSort.binary_search(arr, key, 0, i)

            # Shift elements to make space for key
            if j < i:
                # Store key
                temp = key

                # Shift elements from j to i-1 one position to the right
                for k in range(i, j, -1):
                    arr[k] = arr[k-1]

                # Insert key at position j
                arr[j] = temp
