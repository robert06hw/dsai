def score(item, bins):
    feasible_mask_1 = bins >= item
    target_distance_2 = 100 - bins
    where_value_3 = np.where(feasible_mask_1, target_distance_2, 0)
    max_score = np.max(where_value_3)
    feasible_mask_2 = where_value_3 == max_score
    return np.where(feasible_mask_2, where_value_3, 0)
