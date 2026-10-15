import numpy as np

def score(item, bins):
    target_distance_1 = (100.0 - bins)
    maximum_value_2 = np.maximum(0.0, target_distance_1)
    return maximum_value_2
