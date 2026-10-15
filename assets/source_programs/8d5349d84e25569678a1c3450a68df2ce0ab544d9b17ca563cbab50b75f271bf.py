import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.where(v1 >= 0, v1, 0)  # Ensure v2 is non-negative
    v3 = -(v2 ** 2)
    return v3
