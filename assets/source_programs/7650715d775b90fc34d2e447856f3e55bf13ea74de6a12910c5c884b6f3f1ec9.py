import numpy as np

def score(item, bins):
    bin_scores = np.where(bins >= item, bins - item - 15.0, 0)
    bin_scores = bin_scores ** 3 + bin_scores + 15.0
    return bin_scores
