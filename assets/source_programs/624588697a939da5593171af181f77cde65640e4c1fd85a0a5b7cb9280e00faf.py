import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.where(v1 > 0, v1 ** 2, 0)
    v3 = np.where(v2 > 0, v2 ** 2, 0)
    v4 = np.where(v3 > 0, v3 - 25.0, 0)
    v5 = np.sum(v4)
    v6 = -(v5)
    v7 = (v6 * v2)
    return v7
