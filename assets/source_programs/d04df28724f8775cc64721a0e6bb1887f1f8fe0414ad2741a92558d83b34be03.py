import numpy as np

def score(item, bins):
    v1 = bins >= item
    v2 = np.where(v1, bins - item, 0)
    v3 = v2 ** 3
    v4 = -v3
    return v4
