import numpy as np

def score(item, bins):
    residual = bins - item
    return np.maximum(residual, 0)
