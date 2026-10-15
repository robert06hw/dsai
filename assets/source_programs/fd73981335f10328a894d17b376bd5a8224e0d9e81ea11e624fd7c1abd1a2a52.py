import numpy as np

def score(item, bins):
    v1 = np.where(bins - item >= 0, bins - item, 0)
    v2 = np.where(v1 - 5.0 >= 0, v1 - 5.0, 0)
    v3 = v2 * v2
    v4 = -v3
    return v4
