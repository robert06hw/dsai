def score(item, bins):
    feasible_mask = (bins >= item) & (100.0 - bins > 0)
    capacity_mask = (bins - item) < 1e-9  # epsilon for numerical stability
    feasible_bins = feasible_mask & capacity_mask
    score_bins = np.where(feasible_bins, 1, 0)
    return score_bins
