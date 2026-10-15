import numpy as np

def score(item, bins):
    capacity = 100
    scores = np.max(np.stack((bins - item, capacity - bins)), axis=0)
    return scores
