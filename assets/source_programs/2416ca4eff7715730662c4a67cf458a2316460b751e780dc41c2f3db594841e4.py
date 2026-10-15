import numpy as np

def score(item, bins):
    v1 = (bins - item) / 5.0
    return np.multiply(v1, v1)
