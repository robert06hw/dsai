import numpy as np

def score(item, bins):
    v1 = np.where(bins - item >= 5.0, bins - item - 5.0, 0.0) ** 2
    v2 = np.where(bins - item >= 5.0, bins - item, 0.0)
    v3 = np.where(bins - item >= 5.0, bins - item - 5.0, 0.0)
    v4 = np.maximum(0.0, v3 - 5.0)
    v5 = v4 ** 2
    v6 = np.where(v2 >= 5.0, v5, 0.0)
    v7 = -v6
    return v7
