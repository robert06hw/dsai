import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = 0.75 * item
    v3 = v1 - v2
    v4 = v3 * v3
    v5 = np.where(v4 > 0, -v4, 0)
    return v5
