import numpy as np

def score(item, bins):
    capacities = bins - item
    scores = np.where(capacities >= 0, capacities ** 2, -capacities ** 2)
    return scores
