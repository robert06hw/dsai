import numpy as np

def score(item, bins):
    scores = -(((bins - item) * (bins - item)) / (bins + 1.0)) + (0.45 * (bins - item))
    return np.maximum(scores, 0)  # Ensure scores are non-negative, as bins are positive
