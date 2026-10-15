import numpy as np

def score(item, bins):
    capacity = 100
    diff = bins - item
    squared_diff = diff * diff
    scores = (-squared_diff / (bins + 1.0)) + (0.45 * diff)
    return scores
