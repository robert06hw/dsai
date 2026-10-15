import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = v2 * v2
    v4 = v3 * v1
    v5 = -(v4 + 25.0)
    return v5
