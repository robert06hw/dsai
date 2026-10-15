import numpy as np

def score(item, bins):
    capacity = 100
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.maximum(v2 - 25.0, 0)
    v4 = v3 * v3
    v5 = -(v4)
    return v5
