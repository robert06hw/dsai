import numpy as np

def score(item, bins):
    v2 = bins - item
    v3 = np.maximum(v2 - 25.0, 0)
    v4 = np.power(v3, 3)
    v5 = np.where(v2 > 25.0, v4, v2)
    return v5
