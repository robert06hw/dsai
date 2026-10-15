def score(item, bins):
    target_distance_1 = (100.0 - bins)
    feasible_mask_2 = bins >= item
    product_3 = target_distance_1 * feasible_mask_2
    max_product = np.max(product_3)
    return np.where(product_3 == max_product, bins, bins)
