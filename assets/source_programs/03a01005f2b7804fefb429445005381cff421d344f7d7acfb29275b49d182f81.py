import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.clip(v1, 0, 40)
    v3 = v2 * v2
    v4 = -v3
    return v4
