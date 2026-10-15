import numpy as np

def score(item, bins):
    v2 = bins >= item
    v3 = (bins - item)
    v5 = np.maximum(v3 - 5.0, 0.0)
    v7 = v5 ** 2
    v8 = np.where(v2, v7, 0.0)
    v9 = -(v8)
    return v9
