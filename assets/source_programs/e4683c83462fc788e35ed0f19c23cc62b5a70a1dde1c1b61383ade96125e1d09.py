import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.power(v1, 3)
    v3 = -v2
    return v3
