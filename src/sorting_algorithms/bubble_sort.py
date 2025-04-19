"""
Implementación del algoritmo Bubble Sort.

Bubble Sort es un algoritmo de ordenamiento simple que recorre repetidamente la lista,
comparando elementos adyacentes y los intercambia si están en el orden incorrecto.
El proceso se repite hasta que no se necesiten más intercambios, lo que indica que
la lista está ordenada.
"""

def bubble_sort(arr):
    """
    Ordena una lista utilizando el algoritmo Bubble Sort.
    
    Args:
        arr (list): Lista de elementos a ordenar. Los elementos deben ser comparables.
        
    Returns:
        list: Lista ordenada (la misma referencia recibida como parámetro).
    """
    n = len(arr)
    
    # Recorrer todos los elementos del arreglo
    for i in range(n):
        # Últimos i elementos ya están en su lugar
        swapped = False
        
        for j in range(0, n - i - 1):
            # Recorrer el arreglo de 0 a n-i-1
            # Intercambiar si el elemento encontrado es mayor que el siguiente
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # Si no hubo intercambios en esta pasada, el arreglo ya está ordenado
        if not swapped:
            break
            
    return arr


def bubble_sort_optimized(arr):
    """
    Versión optimizada del Bubble Sort que puede detectar si la lista
    ya está ordenada y evitar pasadas innecesarias.
    
    Args:
        arr (list): Lista de elementos a ordenar. Los elementos deben ser comparables.
        
    Returns:
        list: Lista ordenada (la misma referencia recibida como parámetro).
    """
    n = len(arr)
    
    # Inicializar como True para entrar al bucle al menos una vez
    swapped = True
    
    # Realizar pasadas hasta que no haya intercambios
    while swapped:
        swapped = False
        for i in range(1, n):
            if arr[i - 1] > arr[i]:
                arr[i - 1], arr[i] = arr[i], arr[i - 1]
                swapped = True
        # Reducir n porque el elemento más grande ya está en su posición
        n -= 1
        
    return arr