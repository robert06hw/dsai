import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.maximum(v1, 0)  # Ensure v2 is non-negative
    v3 = np.log(v2 + 1)  # Use log for more complex scoring
    v4 = np.exp(v3)  # Exponentiate for scaling
    return v4
