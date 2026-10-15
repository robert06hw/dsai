import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 25.0, 0)
    v3 = v1 * v2
    v4 = np.maximum(v3 - 25.0, 0)
    v5 = -(v4 * v4)
    return v5
