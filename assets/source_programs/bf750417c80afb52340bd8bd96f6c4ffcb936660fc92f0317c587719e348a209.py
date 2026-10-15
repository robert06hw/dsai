import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.square(v1)
    v3 = v2 - 25.0
    v4 = v2 * v3
    v5 = -(v4)
    v6 = v5 / bins
    return v6
