import numpy as np

def score(item, bins):
    scores = np.full_like(bins, -((bins - item) ** 2 * ((bins - item) ** 2 - 25.0)))
    sorted_indices = np.argsort(scores, kind='mergesort')[::-1]
    return scores[sorted_indices]
