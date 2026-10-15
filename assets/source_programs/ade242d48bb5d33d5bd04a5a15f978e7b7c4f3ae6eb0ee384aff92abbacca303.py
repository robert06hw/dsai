import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = v2 * v2
    v4 = v3 * v3
    v5 = -(v4)
    v6 = np.maximum(v5, 0)
    return v6
