import numpy as np

def score(item, bins):
    v1 = np.maximum(bins - item, 0)
    v2 = v1 - 12.0
    v3 = v2 ** 2
    v4 = -v3
    return v4
