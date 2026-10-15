import numpy as np

def score(item, bins):
    capacity = 100
    bin_scores = (bins - item) * ((bins - item) - 25.0)
    bin_scores = np.clip(bin_scores, 0, capacity * 25)  # Ensure scores are non-negative and within capacity range
    bin_scores = np.maximum(bin_scores - capacity * 25, 0)  # Further scale scores for better comparison
    bin_scores = np.maximum(bin_scores - capacity * 25, 0)  # Final scaling
    bin_scores = bins - item
    return bin_scores
