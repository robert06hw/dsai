import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    return -product_2
