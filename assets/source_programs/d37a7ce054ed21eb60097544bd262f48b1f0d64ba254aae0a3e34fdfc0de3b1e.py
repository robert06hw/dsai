import numpy as np

def score(item, bins):
    bin_scores = np.maximum(0, bins - item) - 40.0
    return -bin_scores * bin_scores
