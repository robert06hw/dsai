import numpy as np

def score(item, bins):
    v1 = bins - item > 0
    v2 = np.minimum(bins, item)
    v3 = (v2 - item)
    v4 = np.maximum(v3, 0)
    v5 = (v4 ** 2)
    v6 = -(v5)
    v7 = np.where(v1, v6, 0)
    return v7
