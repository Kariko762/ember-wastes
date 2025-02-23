import random

def determine_yield_size():
    """
    Determines yield size based on a random percentage roll:
    - None (0 items): 20% chance
    - Small (1-3 items): 40% chance
    - Medium (4-6 items): 25% chance
    - Large (7-10 items): 15% chance
    """
    roll = random.random()  # Returns a float between 0.0 and 1.0
    if roll < 0.20:  # 20%
        return "none", 0
    elif roll < 0.60:  # 40% (0.20 to 0.60)
        return "small", random.randint(1, 3)
    elif roll < 0.85:  # 25% (0.60 to 0.85)
        return "medium", random.randint(4, 6)
    else:  # 15% (0.85 to 1.00)
        return "large", random.randint(7, 10)

if __name__ == "__main__":
    # Test the function
    size, count = determine_yield_size()
    print(f"Yield: {size} ({count} items)")