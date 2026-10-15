import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = 0.75 * item
    v3 = v1 - v2
    v4 = np.square(v3)
    v5 = -v4
    return v5
