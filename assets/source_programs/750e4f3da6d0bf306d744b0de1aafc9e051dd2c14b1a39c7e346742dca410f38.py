import numpy as np

def score(item, bins):
    capacity = 100
    v1 = bins - item
    v2 = np.maximum(0, v1)  # Ensure capacities are non-negative
    v3 = np.minimum(v1, capacity - item)
    v4 = np.where(v1 >= 0, v1, v3)  # Choose smaller of remaining capacity or item
    v5 = np.where(v1 >= 0, v3, -v4)  # Calculate score for bins
    return v5
