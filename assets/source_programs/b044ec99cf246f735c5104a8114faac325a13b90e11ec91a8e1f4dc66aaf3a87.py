import numpy as np

def score(item, bins):
    v1 = np.maximum(bins - item, 0)
    v2 = np.maximum(v1 - 25.0, 0)
    v3 = np.maximum(v1 * v2, 0)
    v4 = np.maximum(v3 * v3, 0)
    v5 = -(v4)
    return v5
