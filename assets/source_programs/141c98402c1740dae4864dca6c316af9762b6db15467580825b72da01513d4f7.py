import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1 - 25.0)
    v3 = np.minimum(v1, v2)
    v4 = np.minimum(v3, 0)
    v5 = np.minimum(v4, 0)
    v6 = -(v5)
    return v6
