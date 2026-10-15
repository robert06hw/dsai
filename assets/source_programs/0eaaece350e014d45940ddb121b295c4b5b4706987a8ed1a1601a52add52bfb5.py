import numpy as np

def score(item, bins):
    capacity = 100.0
    v1 = bins - item >= 5.0
    v2 = np.where(v1, item, 0.0)
    v3 = np.where(v1, bins - item, 0.0)
    v4 = np.where(v1, v2 + v3, 0.0)
    v5 = np.where(v1, capacity - v4, 0.0)
    v6 = np.where(v1, v5, 0.0)
    v7 = np.where(v1, v6, 0.0)
    v8 = -(v7)
    return v8
