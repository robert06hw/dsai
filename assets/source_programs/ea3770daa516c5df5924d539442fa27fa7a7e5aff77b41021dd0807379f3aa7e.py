import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    negative_value_3 = np.negative(product_2)
    return negative_value_3
