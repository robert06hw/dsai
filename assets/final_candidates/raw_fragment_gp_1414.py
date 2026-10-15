import numpy as np

def score(item, bins):
    return np.abs(np.where(bins >= item, bins - item - 14.428263953590589, item))
