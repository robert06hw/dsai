import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 20.0, 0)
    v3 = np.square(v2)
    return -v3
