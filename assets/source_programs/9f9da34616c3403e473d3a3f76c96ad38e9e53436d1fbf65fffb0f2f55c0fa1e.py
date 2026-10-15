import numpy as np

def score(item, bins):
    v1 = (bins - item) ** 2
    v2 = -(((bins - item) ** 2) ** 2 - 25.0) * v1
    v3 = np.max(v2)
    v4 = np.where(v2 == v3, bins, np.zeros_like(bins))
    return v4
