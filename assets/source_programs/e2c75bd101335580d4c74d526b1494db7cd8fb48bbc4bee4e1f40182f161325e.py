import numpy as np

def score(item, bins):
    residual = bins - item
    max_residual = np.maximum(residual, 0)
    adjusted_values = max_residual ** 2
    penalties = -(adjusted_values)
    return penalties
