import numpy as np

def score(item, bins):
    residual = bins - item
    adjustments = residual - 15.0
    product_5 = adjustments ** 2 * (adjustments + 1.0)
    negative_penalty_6 = -product_5
    return negative_penalty_6 + np.argmax(residual)
