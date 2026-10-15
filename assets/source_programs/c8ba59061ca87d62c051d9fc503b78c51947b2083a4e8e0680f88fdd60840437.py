import numpy as np

def score(item, bins):
    scores = -np.square(bins - item) + 25.0
    best_bin = np.argmax(scores)
    return np.zeros_like(bins)
