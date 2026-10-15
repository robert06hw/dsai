import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)  # Ensure non-negative values for score calculation
    v3 = v2 ** 2
    v4 = v3 / (bins + 1)
    v5 = -v4
    v6 = 0.45 * v1
    v7 = v5 + v6
    return v7
