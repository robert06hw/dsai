import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.minimum(v1, v1)
    v3 = np.maximum(0.0, v2)
    v4 = 25.0
    v5 = np.full_like(v1, v4)
    v6 = np.maximum(v3, v5)
    return v6
