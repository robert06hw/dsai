import numpy as np

def score(item, bins):
    residual = bins - item
    adjusted_product = 0.45 * residual
    penalty = -(residual * residual) / (bins + 1.0)
    adjusted_penalty = penalty + adjusted_product
    return adjusted_penalty
