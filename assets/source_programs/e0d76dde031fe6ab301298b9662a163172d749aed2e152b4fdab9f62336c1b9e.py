def score(item, bins):
    bins1 = bins - item
    bins2 = bins1 >= 5.0
    bins3 = bins1 >= 0.0
    bins4 = bins2 * bins3
    bins5 = bins4 ** 2
    return -bins5
