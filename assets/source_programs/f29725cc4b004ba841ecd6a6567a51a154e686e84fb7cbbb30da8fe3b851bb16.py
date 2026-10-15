import numpy as np

def score(item, bins):
    residual = bins - item
    negative_penalty_5 = -(residual / item) ** 0.5
    product_6 = 0.3 * residual
    adjustment_7 = negative_penalty_5 + product_6
    return adjustment_7
