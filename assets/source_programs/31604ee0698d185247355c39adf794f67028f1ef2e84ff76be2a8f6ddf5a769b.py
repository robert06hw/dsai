import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 5.0
    v3 = np.maximum(v2, 0)
    v4 = -(v2)
    v5 = v3 * v4
    return v5
