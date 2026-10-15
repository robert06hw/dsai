def score(item, bins):
    v1 = bins - item
    v2 = v1 - 12.0
    v3 = v2 * v2
    v4 = -v3
    v5 = np.maximum(v1, 0)  # Ensure bins are non-negative
    v6 = v5 * v2
    v7 = v6 * v4
    v8 = np.maximum(v7, 0)  # Ensure scores are non-negative
    return v8
