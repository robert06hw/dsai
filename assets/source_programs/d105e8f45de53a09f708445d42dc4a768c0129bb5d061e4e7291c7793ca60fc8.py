import numpy as np

def score(item, bins):
    v1 = np.subtract(bins, item)
    v2 = np.subtract(v1, 5.0)
    v3 = np.multiply(v2, v2)
    v4 = np.negative(v3)
    return v4
