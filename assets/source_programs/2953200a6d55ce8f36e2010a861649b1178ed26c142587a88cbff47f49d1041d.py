import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.minimum(v1, 25)
    v4 = np.where(v1 > 0, 1, 0)
    v5 = v4 * v2 + (1 - v4) * v3
    return v5
