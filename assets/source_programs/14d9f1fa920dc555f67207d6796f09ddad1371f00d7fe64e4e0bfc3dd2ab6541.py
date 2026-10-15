import numpy as np

def score(item, bins):
    capacity = 100
    scores = np.where(bins >= item, (bins - item) * (bins - item) / (capacity - item), -np.inf)
    return scores
