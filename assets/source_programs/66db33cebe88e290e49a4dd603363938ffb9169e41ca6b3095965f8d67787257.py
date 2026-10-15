def score(item, bins):
    residual = bins - item
    distance_2 = residual - 25.0
    maximum_value = np.maximum(distance_2, 0)
    score = maximum_value * maximum_value * maximum_value
    return score
