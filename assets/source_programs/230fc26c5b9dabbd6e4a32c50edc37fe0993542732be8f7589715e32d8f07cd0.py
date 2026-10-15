import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    normalized_penalty_4 = product_2 / (bins + 1.0)
    adjustment_3 = -(normalized_penalty_4 + 0.45 * residual)
    return adjustment_3
