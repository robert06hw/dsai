import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.where(v1 < 0, 0, v1) + 1.0
    v3 = item / v2
    v4 = np.maximum(v1 - v3, 0)
    v5 = v4 * v4
    v6 = -v5
    return v6
