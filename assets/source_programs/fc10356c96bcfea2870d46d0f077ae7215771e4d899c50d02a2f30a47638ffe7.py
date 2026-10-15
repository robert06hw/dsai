import numpy as np

def score(item, bins):
    v1 = bins - item > 0
    v2 = bins - item
    v3 = np.where(v1, v2, 0.0)
    v4 = v3 / 100.0
    v5 = v4 ** 2
    v6 = -v5
    return v6
