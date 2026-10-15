import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1 - 20.0)
    v3 = v2 * v2
    v4 = np.maximum(0, v3)
    return v4
