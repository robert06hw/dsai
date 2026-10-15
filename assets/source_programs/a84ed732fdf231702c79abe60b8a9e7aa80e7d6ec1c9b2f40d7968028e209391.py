import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * np.where(v1 < 20.0, 1.0, 0.0)
    v3 = v2 * v2
    v4 = -(v3)
    return v4
