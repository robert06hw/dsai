def score(item, bins):
    residual = bins - item
    product = residual * np.log(1 + residual)
    max_value = np.maximum(product, 0)
    return max_value
