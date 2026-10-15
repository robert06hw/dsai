import numpy as np

def score(item, bins):
    v1 = 100.0 - bins
    v2 = bins >= item
    v3 = np.where(v2, v1, 0.0)
    return v3
