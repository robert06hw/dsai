import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.maximum(v1, 0)
    v3 = np.power(v2, 3)
    v4 = -v3
    return v4
