import numpy as np

def score(item, bins):
    return np.where(bins >= item, -(((bins - item) - (1.25 * item)) * ((bins - item) - (1.25 * item))), 0)
