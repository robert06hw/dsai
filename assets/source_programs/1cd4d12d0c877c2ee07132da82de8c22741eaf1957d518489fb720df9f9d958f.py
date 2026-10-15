import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = np.minimum(v2, 0)
    return v3
