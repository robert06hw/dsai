import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 25.0
    v3 = v1 * v2
    v4 = v3 * v3
    v5 = np.maximum(0, np.log(v4) - np.log(100))
    return v5
