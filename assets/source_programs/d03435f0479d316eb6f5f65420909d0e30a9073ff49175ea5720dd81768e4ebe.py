import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    negative_penalty_3 = np.minimum(product_2, 0)
    return negative_penalty_3
