import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1 - 25.0)
    v3 = np.power(v2, 3)
    v4 = -v3
    return v4
