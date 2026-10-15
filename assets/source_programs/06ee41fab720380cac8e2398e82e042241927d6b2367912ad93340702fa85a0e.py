import numpy as np

def score(item, bins):
    capacities = bins - item
    scores = -(capacities - 15.0) ** 2 * (capacities - 15.0 + 1.0)
    max_index = np.argmax(scores)
    return np.where(bins - item == capacities[max_index], np.max(capacities) + 1, bins)
