def score(item, bins):
    # Calculate the difference between each bin capacity and the item size
    diff = bins - item
    
    # Apply the modified scoring function
    score = -np.square(diff) / (bins + 1.0) + 0.45 * diff
    
    return score
