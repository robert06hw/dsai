import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 15.0
    v3 = v2 * v2
    v4 = -(v3)
    v5 = v2 + 1.0
    v6 = v4 * v5
    v7 = np.argmax(v1)
    return v6 + v7
