import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.where(residual >= 25, residual - 25, 0)
    product_3 = residual * target_distance_2
    product_4 = product_3 * product_3
    negative_penalty_5 = -np.where(product_4 >= 1000000, 0, product_4)
    return negative_penalty_5
