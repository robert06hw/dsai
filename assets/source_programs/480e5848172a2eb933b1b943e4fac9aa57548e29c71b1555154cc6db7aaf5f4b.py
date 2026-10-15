import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = (v1 - 25.0)
    v3 = np.maximum(v2, 0)
    v4 = (v1 * v3)
    v5 = (v4 * v4)
    v6 = np.minimum(v5, 0)
    v7 = -(v6)
    return v7
