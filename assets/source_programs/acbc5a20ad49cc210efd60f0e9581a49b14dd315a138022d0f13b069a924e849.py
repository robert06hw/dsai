import numpy as np

def score(item, bins):
    capacities = 100.0 - bins
    valid_bins = capacities >= item
    scores = capacities * valid_bins
    max_score = np.max(scores)
    return np.where(scores == max_score, 1, 0)
