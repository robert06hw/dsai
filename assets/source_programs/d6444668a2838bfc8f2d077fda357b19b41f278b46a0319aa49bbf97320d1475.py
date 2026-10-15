import numpy as np

def score(item, bins):
    v1 = bins >= 5.0
    v2 = bins - item >= 5.0
    v3 = bins - item
    v4 = v3 - 5.0
    v5 = np.where(v2, v4, 0.0)
    v6 = v5 * v5
    v7 = v6
    v8 = -(v7)
    return v8
