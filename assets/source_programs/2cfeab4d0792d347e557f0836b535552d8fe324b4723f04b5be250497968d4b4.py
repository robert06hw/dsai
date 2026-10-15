import numpy as np

def score(item, bins):
    scores = ((bins - item) - 28.0) * ((bins - item) - 28.0)
    sorted_indices = np.argsort(scores)
    best_bin_index = sorted_indices[0]
    scores_sorted = scores[sorted_indices]
    best_score = scores_sorted[0]
    return np.where(bins == bins[best_bin_index], best_score, bins)
