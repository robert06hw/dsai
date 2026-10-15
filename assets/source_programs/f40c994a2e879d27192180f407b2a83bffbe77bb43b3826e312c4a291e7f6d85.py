import numpy as np

def score(item, bins):
    # Calculate the difference between bins and item
    diff = bins - item
    
    # Calculate the squared difference and multiply it by itself
    squared_diff = diff * diff
    
    # Calculate the product of squared differences
    product = squared_diff * squared_diff
    
    # Return the negative of the product
    return -product
