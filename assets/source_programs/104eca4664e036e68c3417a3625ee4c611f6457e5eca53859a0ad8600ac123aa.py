import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.square(v1)
    v3 = -(v2)
    v4 = (v3 + 25.0)
    v5 = np.maximum(v4, 0)
    return v5
