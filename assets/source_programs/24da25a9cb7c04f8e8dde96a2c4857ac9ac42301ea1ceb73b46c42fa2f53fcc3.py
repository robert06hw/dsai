import numpy as np

def score(item, bins):
    capacity = 100.0
    v1 = bins - item
    v2 = v1 - 40.0
    v3 = v2 * v2
    v4 = -(v3)
    return v4
