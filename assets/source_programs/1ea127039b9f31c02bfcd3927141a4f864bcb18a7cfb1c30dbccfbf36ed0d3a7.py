import numpy as np

def score(item, bins):
    v1 = bins - item >= 5.0
    v2 = bins - item >= 0.0
    v3 = np.where(v1, v2, 0)
    v4 = v3 ** 2
    v5 = -(v4)
    return v5
