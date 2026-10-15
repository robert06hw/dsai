import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = np.where(v2 >= 0, v2, 0)
    v4 = np.where(v3 >= 0, v3, 0)
    return v4
