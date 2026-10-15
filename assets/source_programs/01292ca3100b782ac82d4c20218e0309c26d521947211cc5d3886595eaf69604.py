import numpy as np

def score(item, bins):
    residual = bins - item
    max_index = np.argmax(residual)
    return np.zeros_like(bins)
