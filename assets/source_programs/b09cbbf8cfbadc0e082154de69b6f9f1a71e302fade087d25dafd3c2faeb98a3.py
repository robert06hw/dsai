import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 25.0, 0.0)
    v3 = np.maximum(v1 - 50.0, 0.0)
    v4 = -(v3)
    return v4
