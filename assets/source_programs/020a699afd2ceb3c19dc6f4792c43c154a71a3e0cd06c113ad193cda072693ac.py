import numpy as np

def score(item, bins):
    # Calculate the distance from item to the bin capacity
    v1 = bins - item
    # Calculate the squared distance from item to the bin capacity
    v3 = v1 * v1
    # Use numpy vector operations to compute the score
    return -np.sqrt(v3)
