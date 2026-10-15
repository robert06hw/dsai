def score(item, bins):
    feasible_mask_1 = bins >= item
    target_distance_2 = (100.0 - bins)
    where_value_3 = np.where(feasible_mask_1, target_distance_2, 0.0)
    return where_value_3
