import numpy as np

def score(item, bins):
    v1 = bins >= item
    v2 = bins - item
    v3 = np.where(v1, v2, 0)
    v4 = v3 ** 3
    v5 = -(v4)
    v6 = v5 + np.arange(bins.shape[0])[:, None]
    v7 = np.max(v6, axis=1)
    return np.argmax(v6, axis=1)
