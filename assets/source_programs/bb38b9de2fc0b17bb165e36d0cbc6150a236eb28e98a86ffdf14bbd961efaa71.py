import numpy as np

def score(item, bins):
    v1 = np.where(bins >= item, 100.0 - bins, 0.0)
    v2 = np.maximum(0.0, v1)
    return v2
