import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 28.0
    v3 = np.multiply(v2, v2)
    v4 = np.multiply(v3, -1.0)
    return v4
