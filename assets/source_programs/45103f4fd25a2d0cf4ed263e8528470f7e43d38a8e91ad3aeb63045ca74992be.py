import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.clip(v1, 0, 5)
    v3 = v2 * v2
    return -v3
