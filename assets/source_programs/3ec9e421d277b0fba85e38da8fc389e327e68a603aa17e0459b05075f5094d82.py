import numpy as np

def score(item, bins):
    residual = bins - item
    squared_residual = np.square(residual)
    negative_penalty = -np.maximum(squared_residual - 10.0, 0)
    return negative_penalty
