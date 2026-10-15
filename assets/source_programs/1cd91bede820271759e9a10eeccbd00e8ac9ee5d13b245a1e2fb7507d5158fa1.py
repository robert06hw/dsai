import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.clip(v1, 0, 5)
    v3 = np.square(v2)
    return -v3
