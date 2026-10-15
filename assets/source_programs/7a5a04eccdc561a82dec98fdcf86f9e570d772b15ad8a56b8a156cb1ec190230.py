import numpy as np

def score(item, bins):
    capacity = 100.0
    v1 = capacity - bins
    v2 = bins >= item
    v3 = v1 * v2
    return v3
