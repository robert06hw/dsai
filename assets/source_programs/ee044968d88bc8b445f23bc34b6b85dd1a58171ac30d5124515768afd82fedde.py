import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.full_like(v1, -25.0)
    v3 = np.maximum(v2, v1)
    v4 = np.minimum(v1, v3)
    v5 = -v4
    return v5
