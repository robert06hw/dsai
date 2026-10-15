import numpy as np

def score(item, bins):
    return -np.power(np.where(bins >= item, bins - item, 0), 3)
