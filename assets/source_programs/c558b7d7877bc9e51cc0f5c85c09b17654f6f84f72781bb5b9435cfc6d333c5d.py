import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = v2 / (bins + item)
    v4 = np.sqrt(v3)
    v5 = v4 - 1.0
    return v5
