import numpy as np

def score(item, bins):
    return -np.sum(((bins - item) ** 2) ** 2 - 25.0) * (bins - item) ** 2
