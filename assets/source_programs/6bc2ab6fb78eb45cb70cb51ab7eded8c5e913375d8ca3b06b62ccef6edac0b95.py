import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 18.0
    v3 = v2 * v2
    v4 = -v3
    v5 = bins + 1.0
    return v4 / v5
