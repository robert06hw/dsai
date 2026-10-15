import numpy as np

def score(item, bins):
    bin_scores = (-(((bins - item) * (bins - item)) / (bins + 1.0))) + (0.45 * (bins - item))
    # Use numpy's argmax to find the index of the highest score
    best_bin_index = np.argmax(bin_scores)
    # Reduce the number of bins used by setting all other bins to the best score
    return np.where(bins == bins[best_bin_index], bin_scores, np.max(bin_scores))
