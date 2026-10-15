import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.clip(v1 - 25.0, 0, np.inf)
    v3 = v1 * v2
    v4 = np.clip(v3 * v3, 0, np.inf)
    v5 = -v4
    return v5
