def bubble_sort(arr):
    """
    Ordena una lista usando el algoritmo de ordenamiento burbuja (Bubble Sort).

    :param arr: Lista de elementos a ordenar.
    :return: Lista ordenada.
    """
    n = len(arr)
    for i in range(n):
        # Bandera para detectar si hubo un intercambio
        swapped = False
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        # Si no hubo intercambios, la lista ya está ordenada
        if not swapped:
            break
    return arr