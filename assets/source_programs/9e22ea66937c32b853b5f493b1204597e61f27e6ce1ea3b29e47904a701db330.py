import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)  # Ensure v2 is non-negative
    v3 = v2 ** 2
    v4 = v3 - 25.0
    v5 = v4 * v2
    v6 = -v5
    return v6
