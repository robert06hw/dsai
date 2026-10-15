import numpy as np

def score(item, bins):
    return np.where(bins >= item, np.minimum(100.0, bins - item), 0.0)
