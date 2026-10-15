import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = 0.75 * item
    v3 = v1 - v2
    v4 = v3 * v3
    v5 = -v4
    return np.where(v5 > 0, v5, 0)
