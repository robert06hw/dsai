import numpy as np

def score(item, bins):
    residual = bins - item
    max_score = np.max(residual)
    score_bins = np.where(residual == max_score, 1, 0)
    return score_bins
