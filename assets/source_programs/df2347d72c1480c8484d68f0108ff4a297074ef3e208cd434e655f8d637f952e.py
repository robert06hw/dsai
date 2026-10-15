import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 15.0
    v3 = np.where(v2 >= 0, v2 * v2, 0)
    v4 = -(np.where(v3 > 0, v3, 0))
    v5 = bins + 1.0
    v6 = np.where(v5 > 0, v4 * v5, 0)
    return v6
