import numpy as np

def score(item, bins):
    residual = (bins - item)
    normalized_penalty_4 = (residual * residual) / (bins + 1.0)
    negative_penalty_5 = -(normalized_penalty_4)
    product_6 = (0.45 * residual)
    adjustment_7 = (negative_penalty_5 + product_6)
    return adjustment_7
