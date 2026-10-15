import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 5.0, 0)
    v3 = np.maximum(v2 * v2, 0)
    v4 = -(v3)
    return v4
