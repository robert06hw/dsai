import numpy as np

def score(item, bins):
    v1 = bins - item > 0
    v2 = (bins - item)
    v3 = (v2 - 5.0)
    v4 = np.where(v1, v3, 0.0)
    v5 = (v4 * v4)
    v6 = -(v5)
    return v6
