import numpy as np

def score(item, bins):
    v1 = bins >= item
    v2 = bins - item
    v3 = np.where(v1, v2, 0)
    v4 = np.where(v1, v3 ** 2, 0)
    v5 = -(v4)
    return v5
