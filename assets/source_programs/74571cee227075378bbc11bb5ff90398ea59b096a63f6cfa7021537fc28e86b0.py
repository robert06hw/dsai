import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 25.0
    v3 = v1 * v2
    v4 = v3 * v3
    v5 = np.where(v4 < 0, -v4, v4)
    return v5
