def score(item, bins):
    feasible_mask_1 = bins >= item
    zeros_like_value_2 = np.zeros_like(bins)
    where_value_3 = np.where(feasible_mask_1, bins, zeros_like_value_2)
    return where_value_3
