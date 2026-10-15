def score(item, bins):
    residual = bins - item
    adjustment_7 = -0.2 * residual + (bins + 1.0) * residual**2 / 100.0
    return adjustment_7
