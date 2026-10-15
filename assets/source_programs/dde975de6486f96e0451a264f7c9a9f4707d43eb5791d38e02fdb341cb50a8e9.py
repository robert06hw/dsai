import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = v2 / (bins + 1.0)
    v4 = np.where(v2 < 0, 0, v3)
    v5 = np.where(v1 < 0, v1, 0)
    v6 = 0.45 * v1
    v7 = np.where(v2 < 0, v5, v6)
    return v7
