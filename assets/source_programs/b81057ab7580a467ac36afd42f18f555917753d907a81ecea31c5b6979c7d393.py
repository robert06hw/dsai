import numpy as np

def score(item, bins):
    return -np.where(bins >= item, ((bins - item) ** 2 * ((bins - item) ** 2 - 25.0)), bins)
