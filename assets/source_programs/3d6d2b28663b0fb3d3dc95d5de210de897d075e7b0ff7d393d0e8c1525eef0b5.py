import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = (v1 - 25.0)
    v3 = np.clip(v1 * v2, 0, np.inf)
    v4 = np.clip(v3 * v3, 0, np.inf)
    v5 = -(v4)
    return v5
