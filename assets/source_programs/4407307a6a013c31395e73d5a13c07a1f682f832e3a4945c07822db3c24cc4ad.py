import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.where(v1 > 0, v1 - 20.0, 0.0)
    v3 = v2 * v2
    v4 = -np.where(v3 > 0, v3, 0.0)
    return v4
