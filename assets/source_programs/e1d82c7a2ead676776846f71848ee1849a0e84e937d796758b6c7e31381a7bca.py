import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = v2 - 40.0
    v4 = v3 * v3
    return np.where(v4 < 0, 0, v4)
