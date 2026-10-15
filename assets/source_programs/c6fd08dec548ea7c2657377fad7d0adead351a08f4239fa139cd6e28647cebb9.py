import numpy as np

def score(item, bins):
    score_bins = bins - item
    score_bins = np.where(score_bins < 0, 0, score_bins)
    score_bins = score_bins ** 2
    return -score_bins
