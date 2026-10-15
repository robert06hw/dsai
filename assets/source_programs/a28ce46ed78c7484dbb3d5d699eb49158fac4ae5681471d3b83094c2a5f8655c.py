import numpy as np

def score(item, bins):
    residual = bins - item
    distances_2 = residual - 18.0
    squared_distances = distances_2 * distances_2
    negative_penalties = -squared_distances
    adjustments = bins + 1.0
    normalized_penalties = negative_penalties / adjustments
    return normalized_penalties
