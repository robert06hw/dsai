import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.maximum(v2, 0) * item
    v4 = np.maximum(v3, 0) * item * item
    v5 = -v4
    return v5
