import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 25.0, 0)
    return v2
