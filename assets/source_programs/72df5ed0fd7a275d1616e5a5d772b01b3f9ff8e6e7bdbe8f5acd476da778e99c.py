import numpy as np

def score(item, bins):
    v1 = bins >= item + 5.0
    v2 = bins >= item
    v3 = bins - item
    v4 = np.maximum(0.0, v3 - 5.0)
    v5 = v4 * v4
    v6 = v5 * np.where(v2, 1, 0)
    return -(v6)
