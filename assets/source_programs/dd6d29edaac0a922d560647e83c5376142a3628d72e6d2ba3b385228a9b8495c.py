import numpy as np

def score(item, bins):
    return -np.where(bins < item, np.inf, ((bins - item) - 28.0) * ((bins - item) - 28.0))
