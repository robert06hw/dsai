import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1)
    v3 = v2 - 25.0
    v4 = np.maximum(0, v3)
    v5 = v2 * v4
    v6 = v5 * v5
    v7 = -v6
    return v7
