import numpy as np

def score(item, bins):
    residual = bins - item
    distances = np.sqrt(residual ** 2 + 25.0 ** 2)  # Euclidean distance to the nearest bin
    scores = -distances
    return scores
