def score(item, bins):
    residual = bins - item
    adjusted_residual = np.maximum(residual, 0)
    product_2 = adjusted_residual * adjusted_residual
    product_3 = 0.3 * product_2
    adjusted_product_3 = np.maximum(product_3, 0)
    return adjusted_product_3
