import numpy as np

def score(item, bins):
    v1 = bins - item >= 5.0
    v2 = bins - item >= 0.0
    v3 = np.where(v1, 1, 0) * np.where(v2, 1, 0)
    v4 = np.where(v3 > 0, v3**2, 0)
    v5 = np.where(v4 > 0, -v4, 0)
    return v5
