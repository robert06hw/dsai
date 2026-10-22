import numpy as np

def score(item, bins):
    v1 = (bins - item) * (bins - item - 25.0) < 0
    v2 = (bins - item)
    v3 = (v2 - 25.0)
    v4 = (v2 * v3)
    v5 = (v4 * v4)
    v6 = -(v5)
    v7 = np.where(v1, v6, 0)
    return v7
