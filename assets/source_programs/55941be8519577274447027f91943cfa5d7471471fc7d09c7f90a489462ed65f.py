import numpy as np

def score(item, bins):
    v1 = bins >= item + 5.0
    v2 = bins >= item
    v3 = bins - item
    v4 = v3 - 5.0
    v5 = np.maximum(v4, 0.0)
    v6 = v5 ** 2
    v7 = np.where(v2, v6, 0.0)
    v8 = np.where(v1, v7, 0.0)
    v9 = -v8
    return v9
