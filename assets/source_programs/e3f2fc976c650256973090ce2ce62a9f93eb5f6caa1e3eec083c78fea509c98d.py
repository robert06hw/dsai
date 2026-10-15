import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    product_6 = 0.45 * residual
    adjusted_penalty = -(product_2 / (bins + 1.0)) + product_6
    return adjusted_penalty
