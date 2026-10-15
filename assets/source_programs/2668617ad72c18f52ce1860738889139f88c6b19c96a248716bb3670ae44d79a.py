import numpy as np

def score(item, bins):
    residual = bins - item
    adjusted_residual = residual * (bins + 1.0)
    negative_penalty = -adjusted_residual
    product_6 = 0.45 * residual
    adjusted_penalty = negative_penalty + product_6
    return adjusted_penalty
