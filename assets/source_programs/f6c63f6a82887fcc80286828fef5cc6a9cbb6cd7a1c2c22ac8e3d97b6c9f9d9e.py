import numpy as np

def score(item, bins):
    residual = bins - item
    distances = np.maximum(residual - 5.0, 0.0)
    distances_square = distances * distances
    return -distances_square
