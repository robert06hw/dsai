import numpy as np

def score(item, bins):
    return -np.power((bins - item) - 20.0, 2.0)
