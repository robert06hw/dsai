import numpy as np

def score(item, bins):
    v1 = np.select([bins >= item, bins < item + 25], [-1, 0], default=1)
    v2 = bins - item
    v3 = v2 - 25
    v4 = v2 * v3
    v5 = v4 * v4
    v6 = -v5
    v7 = np.where(v1 >= 0, v6, 0)
    return v7
