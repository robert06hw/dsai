import numpy as np

def score(item, bins):
    v1 = np.where((bins - item) > 0, 1, 0)
    v2 = np.zeros_like(bins)
    v3 = np.where(v1, bins - item, v2)
    return v3
