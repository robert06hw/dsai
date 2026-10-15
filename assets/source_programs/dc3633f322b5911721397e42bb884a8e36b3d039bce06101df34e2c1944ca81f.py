import numpy as np

def score(item, bins):
    v2 = bins - item
    v3 = np.maximum(v2, 0)
    v4 = v3 - 5.0
    v5 = np.maximum(v4, 0)
    v6 = v5 * v5
    v7 = -v6
    v8 = np.where(v2 < 0, v2, v7)
    return v8
