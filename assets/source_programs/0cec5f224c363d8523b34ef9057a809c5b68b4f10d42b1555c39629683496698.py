import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.square(v1)
    v3 = item + 1.0
    v4 = v2 / v3
    v5 = -v4
    v6 = 0.3 * v1
    v7 = v5 + v6
    return v7
