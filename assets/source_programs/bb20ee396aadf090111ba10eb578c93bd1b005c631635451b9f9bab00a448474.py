import numpy as np

def score(item, bins):
    return np.where(bins >= item, bins - item, 0) * np.where(bins >= item, bins - item - 25, 0) * np.where(bins >= item, bins - item - 25, 0)
