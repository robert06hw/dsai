import numpy as np

def score(item, bins):
    v1 = bins - item
    v5 = -(np.maximum(-(25.0), v1))
    return v5
