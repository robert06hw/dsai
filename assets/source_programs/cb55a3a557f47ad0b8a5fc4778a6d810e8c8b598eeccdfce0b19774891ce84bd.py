import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = -v2
    result = np.where(v3 == np.max(v3), bins, bins - np.argmin(v3) * np.ones_like(v3))
    return result
