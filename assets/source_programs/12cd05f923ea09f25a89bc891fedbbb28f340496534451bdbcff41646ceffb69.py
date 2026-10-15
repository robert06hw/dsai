def score(item, bins):
    # Subtracting item from bins to align with scoring logic
    bins_minus_item = bins - item
    # Calculating the square of (bins - item) - 28.0
    squared_bins_minus_item = bins_minus_item * bins_minus_item
    # Multiplying by -1 to invert the scoring function
    return -squared_bins_minus_item
