import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.clip(v2, 0, 5)
    v4 = np.maximum(v3, 0)
    v5 = np.multiply(v4, v4)
    v6 = np.multiply(v5, -1)
    return v6
