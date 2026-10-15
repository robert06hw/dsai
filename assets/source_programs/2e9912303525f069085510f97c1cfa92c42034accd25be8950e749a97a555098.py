import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1 - 15.0)
    v3 = v2 ** 2
    v4 = v2 + 1.0
    v5 = v3 * v4
    v6 = -v5
    v7 = np.argmax(v1)
    v8 = np.maximum(v7, v7 + v6)
    return v8
