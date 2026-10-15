import numpy as np

def score(item, bins):
    v1 = (100.0 - bins)
    v2 = np.maximum(0.0, v1)
    return v2
