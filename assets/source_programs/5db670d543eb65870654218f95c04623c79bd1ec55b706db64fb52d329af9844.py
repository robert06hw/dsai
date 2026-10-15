import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 28.0
    v3 = np.square(v2)
    v4 = -v3
    return v4
