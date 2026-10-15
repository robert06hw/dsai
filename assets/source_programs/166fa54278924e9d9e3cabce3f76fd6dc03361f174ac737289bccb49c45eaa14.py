def score(item, bins):
    feasible_mask_1 = bins >= item
    adjustment_4 = (feasible_mask_1 * (bins - item) ** 2) - (1 - feasible_mask_1)
    return adjustment_4
