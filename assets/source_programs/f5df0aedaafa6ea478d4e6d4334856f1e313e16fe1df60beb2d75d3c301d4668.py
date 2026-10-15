import numpy as np

def score(item, bins):
    residual = bins - item
    distances = np.where(residual > 0, residual, 12.0)
    target_distances = distances - 12.0
    squared_distances = target_distances * target_distances
    penalties = -squared_distances
    return penalties
