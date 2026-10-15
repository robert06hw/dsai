import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    adjustment_3 = bins + 1.0
    normalized_penalty_4 = product_2 / adjustment_3
    negative_penalty_5 = -normalized_penalty_4
    product_6 = 0.2 * residual
    adjustment_7 = negative_penalty_5 + product_6
    return adjustment_7
