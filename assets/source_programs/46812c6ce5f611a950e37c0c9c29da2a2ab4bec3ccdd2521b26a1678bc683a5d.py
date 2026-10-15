import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = item + 1.0
    v3 = 20.0 / v2
    v4 = v1 - v3
    v5 = v4 * v4
    v6 = -v5
    return v6
