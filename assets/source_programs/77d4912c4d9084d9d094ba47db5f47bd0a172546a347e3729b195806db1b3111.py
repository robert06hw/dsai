import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = np.maximum(0, residual - 15.0)
    product_3 = distance_2 * distance_2
    negative_penalty_4 = -product_3
    adjustment_5 = bins + 1.0
    product_6 = negative_penalty_4 * adjustment_5
    
    # Choose the highest score, breaking ties by the earliest bin index
    indices = np.argsort(product_6)[::-1]
    max_score = product_6[indices[0]]
    
    # Create a new array with the maximum score for all bins
    result = np.full_like(bins, max_score)
    
    return result
