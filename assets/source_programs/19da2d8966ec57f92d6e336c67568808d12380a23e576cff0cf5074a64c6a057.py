import numpy as np

def score(item, bins):
    capacities = bins - item
    return -np.square(capacities - 5.0)
