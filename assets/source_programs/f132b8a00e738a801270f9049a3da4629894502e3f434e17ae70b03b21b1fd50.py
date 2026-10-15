import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.where(v1 >= 0, v1, 0)
    v3 = np.divide(item, v2 + 1)
    v4 = v2 - v3
    v5 = v4 * v4
    v6 = -np.where(v5 >= 0, v5, 0)
    return v6
