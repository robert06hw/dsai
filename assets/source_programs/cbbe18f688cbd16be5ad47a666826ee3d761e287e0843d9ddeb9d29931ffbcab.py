import numpy as np

def score(item, bins):
    return np.where(bins >= item, -(((bins - item) - 12.0) * ((bins - item) - 12.0)), np.inf)
