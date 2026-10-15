import numpy as np

def score(item, bins):
    residual = bins - item
    distances = np.maximum(residual - 5.0, 0)
    squared_distances = distances * distances
    penalties = -squared_distances
    return penalties
