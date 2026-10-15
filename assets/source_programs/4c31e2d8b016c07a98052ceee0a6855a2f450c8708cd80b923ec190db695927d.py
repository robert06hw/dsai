import numpy as np

def score(item, bins):
    v1 = np.where(bins - item >= 5.0, bins - item - 5.0, 0.0) * np.where(bins - item >= 5.0, bins - item - 5.0, 0.0)
    v2 = bins - item >= 5.0
    v3 = (bins - item)
    v4 = (v3 - 5.0)
    v5 = np.where(v2, v4, 0.0)
    v6 = (v5 * v5)
    v7 = np.where(v1, v6, 0.0)
    v8 = -(v7)
    return v8
