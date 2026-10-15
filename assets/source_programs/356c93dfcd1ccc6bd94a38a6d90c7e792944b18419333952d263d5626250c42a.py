import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 ** 2
    v3 = v2 ** 2
    v4 = v3 - 25.0
    v5 = np.sum(v4)
    v6 = -(v5)
    v7 = v6 * v2
    return v7
