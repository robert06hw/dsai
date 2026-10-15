import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1)  # Ensure non-negative values for v2
    v3 = v2 / (bins + 1.0)
    v4 = np.minimum(v1, v3)
    v5 = v4 * v4
    v6 = -(v5)
    return v6
