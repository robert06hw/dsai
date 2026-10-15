import numpy as np

def score(item, bins):
    return np.where(bins >= item, -(np.power(bins - item, 3)), np.inf)
