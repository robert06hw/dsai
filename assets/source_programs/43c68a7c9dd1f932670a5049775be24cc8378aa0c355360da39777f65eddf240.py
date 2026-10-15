import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * np.maximum(v1, 0)
    v3 = v2 * np.maximum(v2, 0)
    v4 = v3 * np.maximum(v3, 0)
    return v4
