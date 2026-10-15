import numpy as np

def score(item, bins):
    v1 = (100.0 - bins)
    v2 = bins >= item
    v3 = v1 * v2
    return v3
