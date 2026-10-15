import numpy as np

def score(item, bins):
    capacity = 100.0
    v1 = (bins - item)
    v2 = (v1 - 5.0)
    v3 = np.maximum(0, v2)
    v4 = (v3 * v3)
    v5 = -(v4)
    v6 = np.maximum(0, v5)
    v7 = np.maximum(0, v6 - 10.0)
    v8 = np.maximum(0, v7 - 5.0)
    v9 = np.maximum(0, v8 - 1.0)
    return v9
