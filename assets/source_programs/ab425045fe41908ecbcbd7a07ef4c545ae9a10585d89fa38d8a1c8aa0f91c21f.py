import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = v2 / (bins + 1.0)
    v4 = -v3
    v5 = 0.45 * v1
    v6 = v5 + v4
    return v6
