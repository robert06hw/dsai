import numpy as np

def score(item, bins):
    residual = bins - item
    bin_scores = np.maximum(0, residual)
    target_distance = bin_scores - 25.0
    bin_scores = np.maximum(0, target_distance)
    product_1 = bin_scores * bin_scores
    product_2 = product_1 * product_1
    return -product_2
