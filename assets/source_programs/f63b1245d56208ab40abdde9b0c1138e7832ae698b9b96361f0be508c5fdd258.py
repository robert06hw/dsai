import numpy as np

def score(item, bins):
    return np.divide(-(bins - item)**3, bins + 1)
