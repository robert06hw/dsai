import numpy as np

def score(item, bins):
    v1 = bins - item > 25.0
    v2 = np.where(v1, bins - item, 0)
    v3 = np.where(v1, (bins - item) - 25.0, v2)
    v4 = np.where(v1, v3 ** 3, 0)
    v5 = np.where(v1, -(v4), v3)
    return v5
