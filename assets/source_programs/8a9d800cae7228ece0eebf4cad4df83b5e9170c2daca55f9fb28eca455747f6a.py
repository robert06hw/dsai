import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.maximum(v1, 0)
    v3 = np.multiply(v2, v2)
    v4 = np.maximum(v3, 0)
    v5 = np.negative(v4)
    return v5
