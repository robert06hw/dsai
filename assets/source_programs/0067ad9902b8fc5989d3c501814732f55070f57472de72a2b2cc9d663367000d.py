import numpy as np

def score(item, bins):
    diff = bins - item
    within_range = np.logical_and(diff >= 0, diff <= 28.0)
    return within_range * ((diff - 28.0) * (diff - 28.0))
