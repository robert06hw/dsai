import numpy as np

def score(item, bins):
    v1 = bins >= item + 5.0
    v2 = bins >= item
    v3 = np.logical_and(v1, v2)
    v4 = np.square(v3)
    v5 = -(v4)
    return v5
