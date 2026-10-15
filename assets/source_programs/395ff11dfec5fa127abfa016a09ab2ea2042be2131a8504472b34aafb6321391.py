import numpy as np

def score(item, bins):
    # Calculate the difference between each bin and the item
    diff = bins - item
    
    # Calculate the squared difference
    squared_diff = diff ** 2
    
    # Subtract 20 from the squared difference
    adjusted_diff = squared_diff - 20.0 ** 2
    
    # Return the result as a numpy array
    return adjusted_diff
