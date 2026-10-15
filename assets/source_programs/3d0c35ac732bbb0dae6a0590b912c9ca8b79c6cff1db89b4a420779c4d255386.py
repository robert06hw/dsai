def score(item, bins):
    feasible_mask = bins >= item
    bins_to_score = bins[feasible_mask]
    target_distance = 100.0 - bins_to_score
    max_score = np.maximum(0.0, target_distance)
    return max_score
