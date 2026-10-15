import numpy as np

def score(item, bins):
    capacity = 100.0
    v1 = bins - item
    v2 = np.maximum(0.0, v1 - capacity / 2.0)
    v3 = v2 * v2
    v4 = -(v3)
    return v4
