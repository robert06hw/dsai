import numpy as np

def score(item, bins):
    bins_diff = bins - item
    bins_diff = np.maximum(0, bins_diff)  # Cap bins_diff to non-negative
    scores = bins_diff / (bins_diff + 1)  # Calculate scores based on capacity
    return scores
