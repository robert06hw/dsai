import numpy as np

def score(item, bins):
    score_values = np.where(bins >= item, bins - item - 20.0, 0.0)
    return -score_values
