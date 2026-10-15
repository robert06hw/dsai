import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(-25.0, v1)
    v3 = np.minimum(v1, v2)
    return -v3
