import numpy as np

def score(item, bins):
    bins_score = np.minimum((bins - item) * np.maximum(bins - item - 25.0, 0) * ((bins - item) * np.maximum(bins - item - 25.0, 0)), 0)
    return bins_score
