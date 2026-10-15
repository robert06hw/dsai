import numpy as np

def score(item, bins):
    v1 = np.maximum(bins - item, 0)
    v2 = np.minimum(bins - item, 0)
    return v2
