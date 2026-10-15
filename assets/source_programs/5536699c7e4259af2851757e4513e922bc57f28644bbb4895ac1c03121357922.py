import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.where(v1 >= 0, v1, 0)
    v3 = -(v2)
    v4 = -(25.0)
    v5 = np.where(v3 < 0, v4, 0)
    v6 = np.maximum(v3, v5)
    return v6
