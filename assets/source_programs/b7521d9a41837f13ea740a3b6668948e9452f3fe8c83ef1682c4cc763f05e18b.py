import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.square(v1)
    v3 = np.sum(v2)
    v4 = -v3
    v5 = v4 * v2
    return v5
