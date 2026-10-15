import numpy as np

def score(item, bins):
    return np.where(bins >= item, np.full_like(bins, 1e15), np.full_like(bins, -np.inf)) - ((bins - item)) * ((bins - item))
