import numpy as np

def score(item, bins):
    v2 = np.maximum(bins - item, 0)
    v3 = np.maximum(v2 - 10.0, 0)
    v4 = np.maximum(v3 - 10.0, 0)
    v5 = (v4 - 10.0)
    v6 = np.maximum(v5, 0)
    v7 = (v2 * v6)
    v8 = np.maximum(v7, 0)
    v9 = (v8 * v8)
    v10 = -(v9)
    return v10
