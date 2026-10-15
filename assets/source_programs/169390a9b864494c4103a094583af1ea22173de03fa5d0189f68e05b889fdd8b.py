import numpy as np

def score(item, bins):
    v1 = np.maximum(bins - item, 0)
    v2 = np.maximum(v1 - 5.0, 0)
    v3 = v2 * v2
    v4 = -v3
    return v4
