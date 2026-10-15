import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.log(v2 + 1.0)
    v4 = np.log(item / (bins - v2))
    v5 = v3 + v4
    return np.maximum(v5, 0)
