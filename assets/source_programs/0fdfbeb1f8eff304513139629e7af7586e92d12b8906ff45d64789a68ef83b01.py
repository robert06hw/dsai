import numpy as np

def score(item, bins):
    return np.where(bins >= item, -(np.square(bins - item)), np.inf)
