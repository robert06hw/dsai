import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)  # Ensure v2 is non-negative
    v3 = v2 * v2
    v4 = v3 * v3
    v5 = -(v4)
    return v5
