import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.clip(residual, 0, 40.0) - 20.0
    product_3 = target_distance_2 ** 2
    return -product_3
