import numpy as np

def score(item, bins):
    capacity = 100.0
    v1 = np.maximum(bins - item, 0.0)
    v2 = np.maximum(v1 - 15.0, 0.0)
    v3 = v2 * v2
    v4 = -v3
    v5 = np.maximum(v2 + 1.0, 0.0)
    v6 = v4 * v5
    return v6
