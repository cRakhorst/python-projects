import random
import math

# Grid configuration
GRID_SIZE = 7

def get_random_number():
    """Generate a random number between 1 and 50."""
    return math.floor(random.random() * 50 + 1)

def get_random_operator():
    """Generate a random operator."""
    operators = ["+", "-", "x"]
    return operators[math.floor(random.random() * 3)]

def generate_puzzle(size):
    """Generate a cross-math puzzle grid with guaranteed correct equations."""
    while True:  # Keep trying until we generate a valid puzzle
        grid: list[list[int | str | None]] = [[None for _ in range(size)] for _ in range(size)]
        
        # Fill random numbers and operators in the grid
        for i in range(size):
            for j in range(size):
                if i == size - 2:
                    # Separator row
                    if j % 2 == 0:
                        grid[i][j] = "="
                    else:
                        grid[i][j] = None
                elif j == size - 2:
                    # Separator column
                    if i % 2 == 0:
                        grid[i][j] = "="
                    else:
                        grid[i][j] = None
                elif i % 2 == 0 and j % 2 == 0:
                    # Number positions
                    grid[i][j] = get_random_number()
                elif i == size - 1 and j == size - 1:
                    # Bottom-right corner - calculate later
                    grid[i][j] = None
                elif i == size - 1 and j % 2 == 0:
                    # Bottom row - numbers
                    grid[i][j] = get_random_number()
                elif i == size - 1 and j % 2 == 1:
                    # Bottom row - operators
                    grid[i][j] = get_random_operator()
                elif j == size - 1 and i % 2 == 0:
                    # Right column - numbers, calculate later
                    grid[i][j] = None
                elif j == size - 1 and i % 2 == 1:
                    # Right column - operators
                    grid[i][j] = get_random_operator()
                elif i % 2 == 1 and j % 2 == 1:
                    # Empty intersections
                    grid[i][j] = None
                elif i % 2 == 0 and j % 2 == 1:
                    # Horizontal operators
                    grid[i][j] = get_random_operator()
                elif i % 2 == 1 and j % 2 == 0:
                    # Vertical operators
                    grid[i][j] = get_random_operator()
        
        # Calculate and fill horizontal results (rightmost column for top rows)
        for i in range(0, size - 2, 2):
            numbers = [grid[i][j] for j in range(0, size - 2, 2)]
            operators = [grid[i][j] for j in range(1, size - 2, 2)]
            result = calculate_line(numbers, operators)
            grid[i][size - 1] = result
        
        # Calculate and fill vertical results (bottom row for left columns)
        for j in range(0, size - 2, 2):
            numbers = [grid[i][j] for i in range(0, size - 2, 2)]
            operators = [grid[i][j] for i in range(1, size - 2, 2)]
            result = calculate_line(numbers, operators)
            grid[size - 1][j] = result
        
        # Calculate bottom-right corner and solve for the operator
        bottom_numbers = [grid[size - 1][j] for j in range(0, size - 2, 2)]
        bottom_operators = [grid[size - 1][j] for j in range(1, size - 2, 2)]
        bottom_result = calculate_line(bottom_numbers, bottom_operators)
        
        # Right column: get all row results and operators
        right_col_numbers = [grid[i][size - 1] for i in range(0, size - 2, 2)]
        right_col_operators = [grid[i][size - 1] for i in range(1, size - 2, 2)]
        
        # Find an operator at position (1, size-1) that makes the right column equation equal to bottom_result
        found = False
        if len(right_col_numbers) >= 2:
            # Try different operators at position (1, size-1), keeping other operators as they are
            for possible_op in ["+", "-", "x"]:
                # Replace the first operator (at position 1, size-1) with possible_op
                test_operators = [possible_op] + right_col_operators[1:] if len(right_col_operators) > 1 else [possible_op]
                result = calculate_line(right_col_numbers, test_operators)
                
                if result == bottom_result:
                    # This operator works!
                    grid[1][size - 1] = possible_op
                    found = True
                    break
        
        if found:
            # Valid puzzle found
            grid[size - 1][size - 1] = bottom_result
            return grid
        # else: No valid operator found, regenerate puzzle

def calculate_line(numbers, operators):
    """Calculate the result of a line given numbers and operators following order of operations."""
    if not numbers:
        return None
    
    if not operators:
        return numbers[0] if len(numbers) == 1 else None
    
    # Create mutable lists to work with
    nums = list(numbers)
    ops = list(operators)
    
    # First pass: handle multiplication and division from left to right
    i = 0
    while i < len(ops):
        if ops[i] == "x":
            result = nums[i] * nums[i + 1]
            nums = nums[:i] + [result] + nums[i+2:]
            ops = ops[:i] + ops[i+1:]
        elif ops[i] == "/":
            result = nums[i] // nums[i + 1] if nums[i + 1] != 0 else 0
            nums = nums[:i] + [result] + nums[i+2:]
            ops = ops[:i] + ops[i+1:]
        else:
            i += 1
    
    # Second pass: handle addition and subtraction from left to right
    result = nums[0]
    for i, op in enumerate(ops):
        if op == "+":
            result += nums[i + 1]
        elif op == "-":
            result -= nums[i + 1]
    
    return result

start = generate_puzzle(GRID_SIZE)

def display_puzzle(grid):
    """Display the cross-math puzzle in a readable grid format."""
    for row in grid:
        display_row = []
        for cell in row:
            if cell is None:
                display_row.append("  ")
            elif isinstance(cell, int):
                display_row.append(f"{cell:2d}")
            elif cell == "=":
                display_row.append(" =")
            else:
                display_row.append(f" {cell}")
        print("  ".join(display_row))

display_puzzle(start)