import numpy as np

def score(item, bins):
    v1 = bins >= item
    v2 = bins >= item + 5.0
    v3 = bins - item
    v4 = np.where(v2, v3 - 5.0, 0.0)
    v5 = v4 * v4
    v6 = np.where(v1, v5, 0.0)
    v7 = np.where(v2, v6, 0.0)
    v8 = -(v7)
    return v8
