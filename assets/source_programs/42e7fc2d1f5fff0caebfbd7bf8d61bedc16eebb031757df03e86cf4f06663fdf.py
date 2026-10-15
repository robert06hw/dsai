import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = -(25.0)
    v3 = np.full_like(v1, v2)
    v4 = np.maximum(v3, v1)
    v5 = np.minimum(v1, v4)
    v6 = -(v5)
    return v6
