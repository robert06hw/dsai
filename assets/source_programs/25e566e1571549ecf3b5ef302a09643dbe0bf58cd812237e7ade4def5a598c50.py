import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    negative_penalty_3 = -product_2
    adjustment_4 = negative_penalty_3 + 25.0
    return adjustment_4
