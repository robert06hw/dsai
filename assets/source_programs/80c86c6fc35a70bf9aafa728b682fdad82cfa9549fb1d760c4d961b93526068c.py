import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.maximum(v1, 0)
    v3 = v2 / 10
    v4 = (v3 - 0.5)
    v5 = np.maximum(v4, 0)
    v6 = -v5
    return v6
