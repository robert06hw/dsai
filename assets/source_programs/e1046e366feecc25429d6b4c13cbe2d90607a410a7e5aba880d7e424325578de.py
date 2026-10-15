import numpy as np

def score(item, bins):
    residual = bins - item
    product_3 = residual * (residual - 25.0)
    product_4 = product_3 * product_3
    negative_penalty_5 = -product_4
    return negative_penalty_5
