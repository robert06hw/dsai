import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 - 18.0
    v3 = np.multiply(v1, v2)
    v4 = np.negative(v3)
    v5 = bins + 1.0
    v6 = np.divide(v4, v5)
    return v6
