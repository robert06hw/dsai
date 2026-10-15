import numpy as np

def score(item, bins):
    return -np.where(item > bins, np.inf, ((bins - item) - 12.0) * ((bins - item) - 12.0))
