def score(item, bins):
    residual = bins - item
    maximum_value = np.maximum(residual, 0)
    adjusted_value = maximum_value + 1
    return adjusted_value
