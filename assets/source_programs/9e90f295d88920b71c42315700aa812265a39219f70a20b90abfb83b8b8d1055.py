import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 15.0, 0.0)
    v3 = v2 * v2
    v4 = -v3
    v5 = bins + 1.0
    v6 = v4 * v5
    return v6
